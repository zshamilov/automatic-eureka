import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    ResponseDto,
    ComplexTypeGetFullView,
    AttributeShortView,
)
from products.Decision.framework.steps.decision_steps_complex_type import (
    complex_type_list,
    get_custom_type,
)
from products.Decision.utilities.custom_type_constructors import (
    generate_attr_type_name,
    attribute_construct,
)


@allure.epic("Пользовательские типы данных")
@allure.feature("Создание пользовательского типа данных")
@pytest.mark.scenario("DEV-15468")
class TestCustomTypeCreate:
    @allure.story("Пользовательский тип должен сохранятся с атрибутами просто типа",
                  "Пользовательский тип сохранен, если все обязательные поля заполнены "
                  "(название типа, создан хотя бы один атрибут, для которого указаны название атрибута, тип)")
    @allure.title(
        "Создать кастомный тип с атрибутом non complex, non array, проверить, что найден"
    )
    @pytest.mark.smoke
    def test_create_custom_type_prim_attr(self, super_user, create_custom_types_gen):
        with allure.step("Создание кастом типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
        with allure.step("Поиск созданного типа"):
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )
            attributes = []
            for attr in complex_type.attributes:
                attributes.append(AttributeShortView.construct(**attr))
            complex_type.attributes = attributes
        with allure.step(
            "Проверка, что тип найден и создался с указанными параметрами"
        ):
            assert (
                complex_type.objectName == type_name
                and complex_type.attributes[0].arrayFlag == False
            )

    @allure.story("Пользовательский тип должен сохранятся с атрибутами, у которых arrayFlag = true")
    @allure.title(
        "Создать кастомный тип с атрибутом non complex, array, проверить, что найден"
    )
    @pytest.mark.smoke
    def test_create_custom_type_array_prim_attr(
        self, super_user, create_custom_types_gen
    ):
        with allure.step("Создание кастом типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name,
                [
                    attribute_construct(
                        True,
                        False,
                    )
                ],
            )
            custom_type_version_id = create_result.uuid
        with allure.step("Поиск созданного типа"):
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )
        with allure.step(
            "Проверка, что тип найден и создался с указанными параметрами"
        ):
            assert (
                complex_type.objectName == type_name
                and complex_type.attributes[0]["arrayFlag"] == True
            )

    @allure.story("Пользовательский тип должен сохраняться, если его атрибуты имеют"
                  " уникальные названия в рамках этого типа")
    @allure.title(
        "Нельзя создать кастомный тип с двумя атрибутами с неуникальным именем"
    )
    @allure.issue("DEV-5130")
    def test_create_custom_type_with_non_unique_attrs(
        self, super_user, create_custom_types_gen
    ):
        with allure.step("Попытка создать кастомный тип с неуникальными атрибутами"):
            type_name = generate_attr_type_name(True, False, True, "")
        with allure.step("Проверка, что клиенту запрещено"):
            with pytest.raises(HTTPError, match="400"):
                assert create_custom_types_gen.try_create_type(
                    type_name, [attribute_construct(), attribute_construct()]
                )

    @allure.story("Пользовательский тип должен сохраняться, если его название уникально")
    @allure.title("Создать два кастомных типа с неуникальным именем")
    @allure.issue("DEV-2929")
    def test_create_custom_types_with_non_unique_names(
        self, super_user, create_custom_types_gen
    ):
        type_list = []
        name_count = 0
        with allure.step("Создание двух кастом типов с одинаковым именем"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_custom_types_gen.create_type(type_name, [attribute_construct()])
            with pytest.raises(HTTPError, match="400"):
                create_custom_types_gen.try_create_type(type_name, [attribute_construct()])
        with allure.step("Получение списка кастом типов"):
            for obj in complex_type_list(super_user).body["content"]:
                type_list.append(ComplexTypeGetFullView.construct(**obj))
            for t in type_list:
                if t.objectName == type_name:
                    name_count += 1
        with allure.step("Проверка, что в списке нет двух типов с одинаковым именем"):
            assert name_count == 1

    @allure.story("Пользовательский тип должен сохранятся с атрибутами комплексного типа (complexFlag = true),"
                  " при этом в поле complexTypeVersionId этого атрибута должна быть указана latest версия"
                  " другого комплексного типа")
    @allure.title("Создать кастом тип с другим кастом типом внутри")
    @pytest.mark.smoke
    def test_create_custom_type_with_custom_type_attribute(
        self, super_user, create_custom_types_gen
    ):
        type_name1 = generate_attr_type_name(True, False, True, "")
        type_name2 = generate_attr_type_name(True, False, True, "")
        with allure.step("Создание кастом типа"):
            create_response: ResponseDto = create_custom_types_gen.create_type(
                type_name1, [attribute_construct()]
            )
            type1_version_id = create_response.uuid
        with allure.step("Создание второго кастом типа с первым внутри"):
            create_response2: ResponseDto = create_custom_types_gen.create_type(
                type_name2,
                [
                    attribute_construct(
                        False, True, "complex_attr", type1_version_id, None
                    )
                ],
            )
            type2_version_id = create_response2.uuid
        with allure.step("Получение информации о втором кастом типе"):
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, type2_version_id).body
            )
        with allure.step("Проверка, что тип найден и внутри него комплексный атрибут"):
            assert (
                complex_type.objectName == type_name2
                and complex_type.attributes[0]["complexFlag"] == True
            )
