import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    ResponseDto,
    CustomAttributeDictionaryShortInfo,
)
from products.Decision.framework.steps.decision_steps_custom_attr_dict import (
    custom_attributes_list,
    create_custom_attribute,
    delete_custom_attribute,
    get_custom_attribute,
)
from products.Decision.tests.diagrams.test_add_diagrams import (
    generate_diagram_name_description,
)
from products.Decision.utilities.dict_constructors import (
    dict_value_construct,
    dict_construct,
)


@allure.epic("Справочники")
@allure.feature("Удаление справочника")
@pytest.mark.scenario("DEV-5628")
class TestCustomAttributesDelete:
    @allure.story("Справочник пропадает из списка справочников после удаления")
    @allure.title("Создать справочник, удалить, проверить, что пропал из списка")
    @pytest.mark.smoke
    def test_delete_custom_attr_not_found_in_list(self, super_user):
        attribute_found = False
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15", dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict"
                + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value],
            )
            create_result: ResponseDto = ResponseDto.construct(
                **create_custom_attribute(super_user, body=custom_attr).body
            )
        with allure.step("Удаление справочника"):
            delete_response = delete_custom_attribute(
                super_user, dict_id=create_result.uuid
            )
        with allure.step("Получение списка справочников"):
            custom_attrs_list = []
            for custom_attribute in custom_attributes_list(super_user).body["content"]:
                custom_attrs_list.append(
                    CustomAttributeDictionaryShortInfo.construct(**custom_attribute)
                )
        with allure.step("Проверка, что удалённый справочник не найден"):
            for custom_attribute in custom_attrs_list:
                if custom_attribute.id == create_result.uuid:
                    attribute_found = True
            assert not attribute_found and delete_response.status == 200

    @allure.story("После удаления справочник нельзя найти по идентификатору")
    @allure.title("Создать справочник, удалить, проверить, что пропал из списка")
    @pytest.mark.smoke
    def test_delete_custom_attr_not_found(self, super_user):
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15", dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict"
                + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value],
            )
            create_result: ResponseDto = ResponseDto.construct(
                **create_custom_attribute(super_user, body=custom_attr).body
            )
        with allure.step("Удаление справочника"):
            delete_custom_attribute(
                super_user, dict_id=create_result.uuid
            )
        with allure.step("Проверка, что справочник не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert get_custom_attribute(
                    super_user, dict_id=create_result.uuid
                )

    @allure.story("Невозможно удалить справочник, связанный с переменной диаграммы")
    @allure.issue("DEV-7759")
    @allure.title("Удалить справочник, связанный с переменной диаграммы")
    @pytest.mark.smoke
    def test_delete_attr_inside_diag(self, super_user, simple_diagram_dict_attr):
        with allure.step("Получение информации о справочнике внутри диаграммы"):
            dict_id = simple_diagram_dict_attr["dict_id"]
        with allure.step("Проверка, что справочник не удалён"):
            with pytest.raises(HTTPError, match="400"):
                assert delete_custom_attribute(super_user, dict_id=dict_id)
