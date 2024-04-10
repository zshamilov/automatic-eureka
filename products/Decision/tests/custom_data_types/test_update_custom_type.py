import glamor as allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import (
    ComplexTypeCreate,
    ResponseDto,
    ComplexTypeGetFullView,
    # AttributeGetFullView,
)
from products.Decision.framework.steps.decision_steps_complex_type import (
    create_custom_type,
    update_custom_type,
    complex_type_list,
    update_custom_type_attributes,
    get_custom_type_attributes,
    create_custom_type_attributes,
    delete_custom_type_attributes,
)
from products.Decision.utilities.custom_type_constructors import (
    generate_attr_type_name,
    attribute_construct,
    type_update_construct,
    update_attribute_construct,
    create_attribute_construct,
)


@allure.epic("Пользовательские типы данных")
@allure.feature("Обновление пользовательского типа данных")
@pytest.mark.scenario("DEV-15468")
class TestCustomTypeUpdate:
    @allure.story("Возможно обновить комплексный тип и новые параметры сохраняются (имя/описание комплексного типа)")
    @allure.title("Обновить название типа, проверить, что обновился")
    @pytest.mark.smoke
    def test_update_custom_type(self, super_user, create_custom_types_gen):
        with allure.step("Создание пользовательского типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            new_type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
        with allure.step("Изменение имени пользовательского типа"):
            update_response = update_custom_type(
                super_user,
                type_id=custom_type_version_id,
                body=type_update_construct(new_type_name, None, custom_type_version_id)
            )
            update_result: ResponseDto = ResponseDto.construct(**update_response.body)
        with allure.step("Проверка, что имя типа обновилось"):
            type_list = []
            for obj in complex_type_list(super_user).body["content"]:
                type_list.append(ComplexTypeGetFullView.construct(**obj))
            assert any(
                [
                    complex_type.objectName == new_type_name
                    and complex_type.versionId == custom_type_version_id
                    for complex_type in type_list
                ]
            )

    @allure.story("Возможно обновить переменные комплексного типа и измененные "
                  "переменные сохраняются(имя/тип переменной)")
    @allure.title("Обновить тип атрибута типа, проверить, что обновился")
    @pytest.mark.smoke
    def test_update_custom_type_attributes_type(
        self, super_user, create_custom_types_gen
    ):
        with allure.step("Создание пользовательского типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
        with allure.step("Получение id атрибута"):
            attributes = get_custom_type_attributes(
                super_user, type_id=custom_type_version_id
            ).body
            attr_id = None
            for attr in attributes:
                if attr["attributeName"] == "int_primitive_attribute":
                    attr_id = attr["attributeId"]
        with allure.step("Изменение типа атрибута"):
            attribute_update_body = update_attribute_construct(
                custom_type_version_id, False, False, "attribute_made_in_test", None, "0", attr_id
            )
            update_attrs_response = update_custom_type_attributes(
                super_user, type_id=custom_type_version_id, body=attribute_update_body
            )
            update_attrs_result: ResponseDto = update_attrs_response.body
        with allure.step("Проверка, что тип атрибута изменился"):
            attributes_update = get_custom_type_attributes(
                super_user, type_id=custom_type_version_id
            ).body
            assert all(attrs["primitiveTypeId"] == "0" for attrs in attributes_update)

    @allure.story("Возможно добавить к уже созданному комплексному типу параметр")
    @allure.title("В кастомный тип с атрибутом добавить новый атрибут")
    @pytest.mark.smoke
    def test_create_custom_type_attributes(self, super_user, create_custom_types_gen):
        with allure.step("Создание пользовательского типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
        with allure.step("Создание атрибута для пользовательского типа"):
            attribute_create_body = create_attribute_construct(
                custom_type_version_id, False, False, "attribute2_made_in_test", None, "0"
            )

            create_attrs_response = create_custom_type_attributes(
                super_user, type_id=custom_type_version_id, body=attribute_create_body
            )

            create_attrs_result: ResponseDto = create_attrs_response.body
        with allure.step("Проверка, что новый атрибут появился"):
            attributes_update = get_custom_type_attributes(
                super_user, type_id=custom_type_version_id
            ).body
            assert len(attributes_update) == 2

    @allure.story("Возможно удалить переменную из комплексного типа")
    @allure.title("Удалить второй атрибут, проверить, что удалён")
    @pytest.mark.smoke
    def test_delete_second_attributes(self, super_user, create_custom_types_gen):
        with allure.step("Создание пользовательского типа"):
            type_name = "ag_test_type" + generate_string()
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
            # attributes: [AttributeGetFullView] = get_custom_type_attributes(super_user, type_id=custom_type_version_id).body
            # attr_id = None
            # for attr in attributes:
            #     if attr["attributeName"] == "attribute_made_in_test":
            #         attr_id = attr["attributeId"]
        with allure.step("Создание атрибута для пользовательского типа"):
            attribute_create_body = create_attribute_construct(
                custom_type_version_id, False, False, "attribute2_made_in_test", None, "0"
            )
            create_attrs_response = create_custom_type_attributes(
                super_user, type_id=custom_type_version_id, body=attribute_create_body
            )
            create_attrs_result: ResponseDto = create_attrs_response.body
            attribute_id = create_attrs_result["uuid"]
        with allure.step("Удаление созданного атрибута"):
            delete_custom_type_attributes(
                super_user, custom_type_version_id, attribute_id
            )
        with allure.step("Проверка, что новый атрибут удалён"):
            attributes_update = get_custom_type_attributes(
                super_user, type_id=custom_type_version_id
            ).body
            assert len(attributes_update) == 1
