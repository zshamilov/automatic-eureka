import random
import string
import uuid

import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    NodeMetaInfo,
    Position,
    ResponseDto,
    NodeViewWithVariablesDto,
    Finish,
    DiagramViewDto,
    NodeUpdateDto, DiagramRename,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version,
    update_diagram_parameters, rename_diagram,
)
from products.Decision.framework.steps.decision_steps_nodes import (
    create_node,
    get_node_by_id,
    delete_node_by_id,
    create_link,
    delete_link_by_id,
    update_node,
)
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.node_cunstructors import (
    node_construct,
    link_construct,
    variables_for_node,
)
from products.Decision.utilities.variable_constructors import variable_construct


@allure.epic("Диаграммы")
@allure.feature("Редактирование диаграммы")
class TestDiagramsEdit:
    @allure.story("Узел можно создать", "Существующий узел можно получить")
    @allure.title("Создать узел, проверить, что создан")
    @pytest.mark.scenario("DEV-5853")
    def test_create_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание узла"):
            node = node_construct(
                142, 202.22915649414062, "start", temp_version_id, None
            )
            node_start: ResponseDto = create_node(super_user, node).body
            node_id = node_start["uuid"]
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = get_node_by_id(
                super_user, node_id
            ).body
        with allure.step("Проверка, что узел найден и создан с указанными параметрами"):
            assert node_view is not None and node_view["nodeName"] == "Начало"

    @allure.story("Узел можно удалить")
    @allure.title("Удалить узел, проверить, что не найден")
    @pytest.mark.scenario("DEV-5853")
    def test_delete_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание узла"):
            node = node_construct(
                142, 202.22915649414062, "start", temp_version_id, None
            )
            node_start: ResponseDto = create_node(super_user, node).body
            node_id = node_start["uuid"]
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert get_node_by_id(super_user, node_id)

    @allure.story("Можно создать связь 2 узлов")
    @allure.title("Создать два узла, связать, проверить, что связь появилась")
    @pytest.mark.scenario("DEV-15448")
    @pytest.mark.smoke
    def test_create_link(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание узла начала"):
            node_start = node_construct(
                142, 202.22915649414062, "start", temp_version_id, None
            )
            node_start_response: ResponseDto = create_node(super_user, node_start).body
            node_start_id = node_start_response["uuid"]
        with allure.step("Создание узла завершения"):
            node_finish = node_construct(
                714, 202.22915649414062, "finish", temp_version_id, None
            )
            node_finish_response: ResponseDto = create_node(
                super_user, node_finish
            ).body
            node_finish_id = node_finish_response["uuid"]
        with allure.step("Создание связи между узлами"):
            link = link_construct(temp_version_id, node_start_id, node_finish_id)
            link_create_response: ResponseDto = create_link(super_user, body=link).body
            link_id = link_create_response["uuid"]
        with allure.step("Получение информации о диаграмме"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, temp_version_id
            )
            diagram: DiagramViewDto = get_diagram_by_version_response.body
        with allure.step("Проверка, что связь появилась в информации о диаграмме"):
            assert diagram["links"][link_id] is not None

    @allure.story("Можно удалить связь 2 узлов")
    @allure.title("Удалить связь, проверить, что пропала")
    @pytest.mark.scenario("DEV-15448")
    @pytest.mark.smoke
    def test_delete_link(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание узла начала"):
            node_start = node_construct(
                142, 202.22915649414062, "start", temp_version_id, None
            )
            node_start_response: ResponseDto = create_node(super_user, node_start).body
            node_start_id = node_start_response["uuid"]
        with allure.step("Создание узла завершения"):
            node_finish = node_construct(
                714, 202.22915649414062, "finish", temp_version_id, None
            )
            node_finish_response: ResponseDto = create_node(
                super_user, node_finish
            ).body
            node_finish_id = node_finish_response["uuid"]
        with allure.step("Создание связи между узлами"):
            link = link_construct(temp_version_id, node_start_id, node_finish_id)
            link_create_response: ResponseDto = create_link(super_user, body=link).body
            link_id = link_create_response["uuid"]
        with allure.step("Удаление связи между узлами"):
            delete_link_by_id(super_user, link_id)
        with allure.step("Получение информации о диаграмме"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, temp_version_id
            )
            diagram: DiagramViewDto = get_diagram_by_version_response.body
        with allure.step(
            "Проверка, что в информации о диограмме отсутствует информация о связях между узлами"
        ):
            assert "links" not in diagram

    @allure.story("Нельзя создать больше одной исходящей связи из всех типов узлов кроме ветвления и fork")
    @allure.title(
        "Попробовать из узла начала протянуть связь до двух узлов завершения, проверить, что неудачно"
    )
    @pytest.mark.scenario("DEV-15448")
    @allure.issue("DEV-7156")
    def test_two_links_unavailable_from_one(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание узла начала"):
            node_start = node_construct(
                142, 202.22915649414062, "start", temp_version_id, None
            )
            node_start_response: ResponseDto = create_node(super_user, node_start).body
            node_start_id = node_start_response["uuid"]
        with allure.step("Создание первого узла завершения"):
            node_finish1 = node_construct(
                714, 202.22915649414062, "finish", temp_version_id, None
            )
            node_finish1_response: ResponseDto = create_node(
                super_user, node_finish1
            ).body
            node_finish1_id = node_finish1_response["uuid"]
        with allure.step("Создание второго узла завершения"):
            node_finish2 = node_construct(714, 500, "finish", temp_version_id, None)
            node_finish2_response: ResponseDto = create_node(
                super_user, node_finish2
            ).body
            node_finish2_id = node_finish2_response["uuid"]
        with allure.step("Создание связи между узлами"):
            link1 = link_construct(temp_version_id, node_start_id, node_finish1_id)
            link1_create_response: ResponseDto = create_link(
                super_user, body=link1
            ).body
            link1_id = link1_create_response["uuid"]
        with allure.step("Создание связи между узлами"):
            link2 = link_construct(temp_version_id, node_start_id, node_finish2_id)
            link2_create_response: ResponseDto = create_link(
                super_user, body=link2
            ).body
            link2_id = link2_create_response["uuid"]
        with allure.step("Получение информации о диаграмме"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, temp_version_id
            )
            diagram: DiagramViewDto = get_diagram_by_version_response.body
        with allure.step(
            "Проверка, что в информации о диаграмме присутствует только одна связь"
        ):
            assert len(diagram["links"]) == 1

    @allure.story("Узел можно обновить")
    @allure.title("Отредактировать узел, увидеть, что информация об узле изменилась")
    @pytest.mark.scenario("DEV-5853")
    def test_update_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание узла завершения"):
            node_finish = node_construct(
                714, 202.22915649414062, "finish", temp_version_id, None
            )
            node_finish_response: ResponseDto = create_node(
                super_user, node_finish
            ).body
            node_finish_id = node_finish_response["uuid"]
        with allure.step("Создание данных параметров"):
            letters = string.ascii_lowercase
            rand_string_param_name = "".join(random.choice(letters) for i in range(8))
            parameter_version_id2 = uuid.uuid4()
        with allure.step("Обновить параметры"):
            params_response = update_diagram_parameters(
                super_user,
                temp_version_id,
                [
                    variable_construct(),
                    variable_construct(
                        array_flag=False,
                        complex_flag=False,
                        default_value=None,
                        is_execute_status=None,
                        order_num=0,
                        param_name=rand_string_param_name,
                        parameter_type="in_out",
                        parameter_version_id=str(parameter_version_id2),
                        type_id=1,
                    ),
                ],
            )

            update_param_response: ResponseDto = params_response.body

        with allure.step("Обновить узел на новый параметр"):
            position = NodeMetaInfo(position=Position(x=714, y=202.22915649414062))
            properties = Finish.construct()
            variables = variables_for_node(
                "finish",
                False,
                False,
                rand_string_param_name,
                1,
                parameter_version_id2,
                None,
                None,
                None,
                None,
            )
            properties.mappingVariables = [variables]
            update_node_response = update_node(
                super_user,
                node_id=node_finish_id,
                body=NodeUpdateDto.construct(
                    nodeTypeId=3,
                    diagramVersionId=temp_version_id,
                    nodeName="Завершение",
                    nodeDescription=None,
                    properties=properties,
                    metaInfo=position,
                ),
            )
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = get_node_by_id(
                super_user, node_finish_id
            ).body
        with allure.step("Проверка, что параметр появился"):
            assert (
                node_view["properties"]["mappingVariables"][0]["variableName"]
                == rand_string_param_name
            )

    @allure.story("Диаграмму можно переименовать")
    @allure.title(
        "Проверка переименования диаграмм"
    )
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_rename_diagram(
            self, super_user, create_temp_diagram, save_diagrams_gen, create_temp_diagram_gen
    ):
        with allure.step("Генерация информации о диаграмме"):
            diagram_name = (
                    "diagram_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_desc = "test"
        with allure.step("Создание template диаграммы"):
            diagram_temp = create_temp_diagram
            diagram_id = diagram_temp["diagramId"]
            temp_version_id = diagram_temp["versionId"]
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(**save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, diagram_name, diagram_desc
            ).body)
            version_id = create_result.uuid
        with allure.step("Переименование диаграммы"):
            diagram_new_name = "diagram_" + generate_diagram_name_description(16, 1)["rand_name"]
            create_result = rename_diagram(
                super_user, version_id, body=DiagramRename(objectName=diagram_new_name)
            )
        with allure.step("Проверка, что искомая диаграмма под новым именем"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, str(version_id)
            )
            diagram: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_by_version_response.body
            )
            assert diagram.objectName == diagram_new_name

    @allure.story("Есть ограничения на длинну имени при переименовании")
    @allure.title("Проверка ограничения на длину имени при переименовании")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.parametrize(
        "name,status",
        [
            (generate_diagram_name_description(99, 1)["rand_name"], 200),
            (generate_diagram_name_description(100, 1)["rand_name"], 200),
        ],
    )
    @pytest.mark.sdi
    def test_rename_diagram_name_length(
            self, super_user, create_temp_diagram, save_diagrams_gen, create_temp_diagram_gen,
            name, status
    ):
        with allure.step("Генерация информации о диаграмме"):
            diagram_name = (
                    "diagram_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_desc = "test"
        with allure.step("Создание template диаграммы"):
            diagram_temp = create_temp_diagram
            diagram_id = diagram_temp["diagramId"]
            temp_version_id = diagram_temp["versionId"]
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(**save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, diagram_name, diagram_desc
            ).body)
            version_id = create_result.uuid
        with allure.step("Переименование диаграммы"):
            diagram_new_name = name
            create_result: ResponseDto = ResponseDto.construct(**rename_diagram(
                super_user, version_id, body=DiagramRename.construct(objectName=diagram_new_name)
            ).body)
        with allure.step("Проверка статуса"):
            assert create_result.httpCode == status

    @allure.story("Есть ограничения на длинну имени при переименовании")
    @allure.title("Проверка ограничения на длину имени при переименовании")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.parametrize(
        "name,status",
        [
            (generate_diagram_name_description(101, 1)["rand_name"], 400),
        ],
    )
    @pytest.mark.sdi
    def test_rename_diagram_name_length_neg(
            self, super_user, create_temp_diagram, save_diagrams_gen, create_temp_diagram_gen,
            name, status
    ):
        with allure.step("Генерация информации о диаграмме"):
            diagram_name = (
                    "diagram_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_desc = "test"
        with allure.step("Создание template диаграммы"):
            diagram_temp = create_temp_diagram
            diagram_id = diagram_temp["diagramId"]
            temp_version_id = diagram_temp["versionId"]
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(**save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, diagram_name, diagram_desc
            ).body)
            version_id = create_result.uuid
        with allure.step("Переименование диаграммы не успешно"):
            diagram_new_name = name
            with pytest.raises(HTTPError, match=f"{status}"):
                assert rename_diagram(
                    super_user, version_id, body=DiagramRename.construct(objectName=diagram_new_name))

    @allure.story("Есть проверка ограничения на недопустимые символы при переименовании")
    @allure.title("Проверка ограничения на недопустимые символы при переименовании")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.parametrize(
        "name,status",
        [
            ("", 400)
        ],
    )
    @pytest.mark.sdi
    def test_rename_diagram_symbols(
            self, super_user, create_temp_diagram, save_diagrams_gen, create_temp_diagram_gen,
            name, status
    ):
        with allure.step("Генерация информации о диаграмме"):
            diagram_name = (
                    "diagram_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_desc = "test"
        with allure.step("Создание template диаграммы"):
            diagram_temp = create_temp_diagram
            diagram_id = diagram_temp["diagramId"]
            temp_version_id = diagram_temp["versionId"]
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(**save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, diagram_name, diagram_desc
            ).body)
            version_id = create_result.uuid
        with allure.step("Переименование диаграммы"):
            diagram_new_name = name
        with allure.step("Проверка статуса"):
            with pytest.raises(HTTPError):
                assert rename_diagram(
                    super_user, version_id, body=DiagramRename.construct(objectName=diagram_new_name)
                ).status == status

