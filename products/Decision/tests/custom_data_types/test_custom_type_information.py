import base64
import random
import string
import uuid

import glamor as allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import (
    ComplexTypeGetFullView,
    ResponseDto,
    ComplexTypeGetFullVersionView,
    ComplexTypePage, ComplexTypeGetTreeView,
)
from products.Decision.framework.steps.decision_steps_complex_type import (
    complex_type_list,
    get_custom_type,
    list_complex_type_versions,
    get_complex_type_map, get_complex_type_tree,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    update_diagram_parameters,
    get_diagrams_related_to_object,
)
from products.Decision.tests.diagrams.test_add_diagrams import (
    generate_diagram_name_description,
)
from products.Decision.utilities.custom_type_constructors import (
    generate_attr_type_name,
    attribute_construct,
)
from products.Decision.utilities.variable_constructors import variable_construct


@allure.epic("Пользовательские типы данных")
@allure.feature("Ионформация о пользовательских типах данных")
class TestCustomTypeInfo:
    @allure.story(
        "Возможно получить список комплексных типов и отображаются необходимые поля"
    )
    @allure.title(
        "Создать кастомный тип с атрибутом non complex, non array, проверить, что появился в списке"
    )
    @pytest.mark.scenario("DEV-15468")
    @pytest.mark.smoke
    def test_get_custom_type_list(self, super_user, create_custom_types_gen):
        type_list = []
        with allure.step("Получение списка кастом типов"):
            for obj in complex_type_list(super_user).body["content"]:
                type_list.append(ComplexTypeGetFullView.construct(**obj))
        with allure.step("Проверка, что в списке содержится необходимая информация"):
            types_contain_req_fields = next(
                (
                    c_type
                    for c_type in type_list
                    if c_type.typeId is not None
                    and c_type.versionId is not None
                    and c_type.objectName is not None
                    and c_type.displayName is not None
                    and c_type.changeDt is not None
                ),
                True,
            )
            assert types_contain_req_fields

    @allure.story(
        "В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber"
    )
    @allure.title(
        "Получить список всех типов, проверить, что totalElements соответствует длине списка"
    )
    @pytest.mark.scenario("DEV-15468")
    @pytest.mark.environment_dependent
    def test_types_total_elements_correct(self, super_user):
        with allure.step("Получение списка типов"):
            type_page: ComplexTypePage = ComplexTypePage.construct(
                **complex_type_list(super_user).body
            )
            assert type_page.totalElements == len(type_page.content)

    @allure.story(
        "В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber"
    )
    @allure.title(
        "Получить список всех типов, проверить, что totalPages соответствует длине списка, делённой на 20 плюс 1"
    )
    @pytest.mark.scenario("DEV-6400")
    @pytest.mark.environment_dependent
    def test_types_total_pages_correct(self, super_user):
        list_query_str = '{"filters":[],"sorts":[],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        with allure.step("Получение списка всех типов"):
            type_page: ComplexTypePage = ComplexTypePage.construct(
                **complex_type_list(super_user).body
            )
        with allure.step("Получение ограниченного списка типов для проверки"):
            type_page1: ComplexTypePage = ComplexTypePage.construct(
                **complex_type_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
            assert type_page1.totalPages == len(type_page.content) // 20 + 1

    @allure.story(
        "В ответе для base64 с параметром page в ответ приходит current page = page-1"
    )
    @allure.title(
        "Получить список типов с заданной страницей, проверить, что текущая страница такая же,"
        " как указано в параметре минус 1")
    @pytest.mark.scenario("DEV-6400")
    @pytest.mark.environment_dependent
    def test_types_current_page_correct(self, super_user):
        page_num = 2
        list_query_str = (
            f'{{"filters":[],"sorts":[],"searchBy":"","page":{page_num},"size":10}}'
        )
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка типов с фильтром по выдаче"):
            type_page: ComplexTypePage = ComplexTypePage.construct(
                **complex_type_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
            assert type_page.currentPageNumber == page_num - 1

    @allure.story(
        "При отсутствии query - кол-во элементов 20, если totalElements не меньше 20"
    )
    @allure.title(
        "Проверка, что возможно получить список типов без указания параметров выдачи"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_types_page_defaults(self, super_user):
        with allure.step("Получение списка типов без указания параметров выдачи"):
            type_page_response = complex_type_list(super_user, query={})
        with allure.step("Проверка, что успешно"):
            assert (
                type_page_response.status == 200
                and len(type_page_response.body["content"]) <= 20
            )

    @allure.story("Возможно получить список версий комплексного типа")
    @allure.title(
        "получить список версий комплексного типа, проверить, что данные корректны"
    )
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_get_custom_type_versions_by_id(self, super_user, create_custom_types_gen):
        with allure.step("Создание кастом типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )
            type_id = complex_type.typeId
        with allure.step("Получение списка версий"):
            versions_body = list_complex_type_versions(super_user, type_id).body
            versions: [ComplexTypeGetFullVersionView] = []
            for version in versions_body:
                versions.append(ComplexTypeGetFullVersionView.construct(**version))
        with allure.step("Проверка, что у версии правильные идентификаторы"):
            assert (
                len(versions) == 1
                and versions[0].versionId == custom_type_version_id
                and versions[0].typeId == type_id
            )

    @allure.story(
        "Возможно получить комплексный тип со всеми вложениями(если внутри есть комплексный тип, "
        "внутри которого есть комплексный тип)*n"
    )
    @allure.title(
        "получить список вложений комплексного типа, проверить, что данные корректны"
    )
    @pytest.mark.scenario("DEV-15468")
    @pytest.mark.smoke
    def test_get_custom_type_map_by_id(self, super_user, create_custom_types_gen):
        with allure.step("Создание кастом типа"):
            type_name1 = generate_attr_type_name(True, False, True, "")
            type_name2 = generate_attr_type_name(True, False, True, "")
            create_response: ResponseDto = create_custom_types_gen.create_type(
                type_name1, [attribute_construct()]
            )
            type1_version_id = create_response.uuid
            create_response2: ResponseDto = create_custom_types_gen.create_type(
                type_name2,
                [
                    attribute_construct(
                        False, True, "complex_attribute", type1_version_id, None
                    )
                ],
            )
            type2_version_id = create_response2.uuid
            complex_type_include: ComplexTypeGetFullView = (
                ComplexTypeGetFullView.construct(
                    **get_custom_type(super_user, type1_version_id).body
                )
            )
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, type2_version_id).body
            )
            type_id = complex_type.typeId
        with allure.step("Получение вложений кастом типа"):
            type_map = get_complex_type_map(super_user, type2_version_id).body
        with allure.step("Проверка, что вложения корректно отображаются"):
            assert (
                type_map[f"{type2_version_id}"]["attributes"][0]["complexTypeVersionId"]
                == type_map[f"{type1_version_id}"]["versionId"]
            )

    @allure.story(
        "Возможно получить комплексный тип со всеми уровнями вложенности в древовидном формате"
    )
    @allure.title(
        "Получить дерево вложений комплексного типа"
    )
    @pytest.mark.scenario("DEV-23445")
    def test_get_custom_type_tree_by_id(self, super_user, create_custom_types_gen):
        with allure.step("Создание кастом типа с двумя уровнями вложенности"):
            type_name3 = "main_type_" + generate_string()
            type_name2 = "inner_type_1_" + generate_string()
            type_name1 = "inner_type_2_" + generate_string()
            create_response: ResponseDto = create_custom_types_gen.create_type(
                type_name1, [attribute_construct()]
            )
            type1_version_id = create_response.uuid
            create_response2: ResponseDto = create_custom_types_gen.create_type(
                type_name2,
                [attribute_construct(False, True, "complex_attribute", type1_version_id, None)],
            )
            type2_version_id = create_response2.uuid
            create_response3: ResponseDto = create_custom_types_gen.create_type(
                type_name3,
                [attribute_construct(False, True, "complex_attribute", type2_version_id, None)],
            )
            type3_version_id = create_response3.uuid
        with allure.step("Получение типа со всеми вложениями в древовидном виде"):
            type_tree: ComplexTypeGetTreeView = get_complex_type_tree(super_user, type3_version_id)
        with allure.step("Древовидная структурая корректна"):
            assert len(type_tree.attributes) == 1
            assert str(type_tree.attributes[0].complexTypeVersionId) == type2_version_id
            assert len(type_tree.attributes[0].complexTypeVersion.attributes) == 1
            assert str(type_tree.attributes[0].complexTypeVersion.attributes[0]
                       .complexTypeVersionId) == type1_version_id
            assert len(type_tree.attributes[0].complexTypeVersion.attributes[0].complexTypeVersion.attributes) == 1
            assert not type_tree.attributes[0].complexTypeVersion.attributes[0].complexTypeVersion.attributes[0].complexFlag


    @allure.story(
        "Можно получить список диаграмм, в которых используется пользовательский тип objectType = COMPLEX_TYPE."
        "Требуется создать диаграмму с пользовательским типом на вход/выход/локальной переменной и проверить её наличие в полученном списке."
    )
    @allure.title("можно найти диаграмму, которая использует кастом тип")
    @allure.issue("DEV-5810")
    @pytest.mark.scenario("DEV-8572")
    @pytest.mark.skip("obsolete")
    def test_custom_type_include_diagram(
        self,
        super_user,
        create_custom_types_gen,
        create_temp_diagram_gen,
        save_diagrams_gen,
    ):
        with allure.step("Создание кастом типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            attr = attribute_construct()
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attr]
            )
            custom_type_version_id = create_result.uuid
        with allure.step("Создание диаграммы с кастом типом в качестве переменной"):
            diagram_template = dict(create_temp_diagram_gen.create_template())
            temp_version_id = diagram_template["versionId"]
            diagram_id = diagram_template["diagramId"]
            letters = string.ascii_lowercase
            rand_string_param_name = "".join(random.choice(letters) for i in range(8))
            parameter_version_id = uuid.uuid4()
            new_var = variable_construct(
                array_flag=False,
                complex_flag=True,
                default_value=None,
                is_execute_status=None,
                order_num=0,
                param_name=rand_string_param_name,
                parameter_type="in_out",
                parameter_version_id=parameter_version_id,
                type_id=custom_type_version_id,
            )
            params_response = update_diagram_parameters(
                super_user, temp_version_id, [variable_construct(), new_var]
            )
            update_response: ResponseDto = params_response.body
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = (
                "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_description = "diagram created in test"
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, new_diagram_name, diagram_description
            ).body
            saved_version_id = create_result["uuid"]
        complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
            **get_custom_type(super_user, custom_type_version_id).body
        )
        type_id = complex_type.typeId
        with allure.step("Получение related diagrams"):
            related_diagrams_response = get_diagrams_related_to_object(
                super_user, "COMPLEX_TYPE", type_id
            )
            related_diagrams_response_body = related_diagrams_response.body
            # related_diagram: ObjectUsedInDiagramFullViewDto = ObjectUsedInDiagramFullViewDto.construct(
            #     **related_diagrams_response_body[0])
        with allure.step("Проверка, что диаграмма верная"):
            assert (
                related_diagrams_response.status == 200
                and related_diagrams_response_body["diagramId"] == diagram_id
                and related_diagrams_response_body["diagramVersionId"]
                == saved_version_id
            )
