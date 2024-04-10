import datetime

import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, CustomAttributeDictionaryShortInfo, \
    CustomAttributeDictionaryFullView
from products.Decision.framework.steps.decision_steps_custom_attr_dict import custom_attributes_list, \
    get_custom_attribute
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct


@allure.epic("Справочники")
@allure.feature("Добавление справочника")
@pytest.mark.scenario("DEV-5628")
class TestCustomAttributesCreate:

    @allure.story("Созданный справочник появляется в списке справочников")
    @allure.title("Создать справочник, проверить, что появился в списке")
    @pytest.mark.smoke
    def test_create_custom_attr_found_in_list(self, super_user, create_dict_gen):
        attribute_found = False
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение списка справочников"):
            custom_attrs_list = []
            for custom_attribute in custom_attributes_list(super_user).body["content"]:
                custom_attrs_list.append(
                    CustomAttributeDictionaryShortInfo.construct(**custom_attribute))
        with allure.step("Проверка, что созданный справочник найден"):
            for custom_attribute in custom_attrs_list:
                if custom_attribute.id == create_result.uuid:
                    attribute_found = True
            assert attribute_found

    @allure.story("Невозможно создать справочник с dictName пустым или длиной <1 или >100")
    @allure.title("Попытаться создать справочники с недопустимыми именами, проверить, что недопустимо")
    @pytest.mark.parametrize('name_len,status', [(99, 201),
                                                 (100, 201)])
    def test_create_custom_attr_name_pos(self, super_user, create_dict_gen, name_len, status):
        dict_name = generate_diagram_name_description(name_len, 1)["rand_name"]
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(dict_name=f"{dict_name}",
                                         dict_value_type_id="1",
                                         values=[value])
            create_result = create_dict_gen.try_create_dict(dict_body=custom_attr)
        with allure.step("Проверка ответа на создание справочника"):
            assert create_result.status == status

    @allure.story("Невозможно создать справочник с dictName пустым или длиной <1 или >100")
    @allure.title("Попытаться создать справочники с недопустимыми именами, проверить, что недопустимо")
    @pytest.mark.parametrize('name_len,status', [(0, 400),
                                                 (101, 400)])
    def test_create_custom_attr_name_negative(self, super_user, create_dict_gen, name_len, status):
        dict_name = generate_diagram_name_description(name_len, 1)["rand_name"]
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(dict_name=f"{dict_name}",
                                         dict_value_type_id="1",
                                         values=[value])
        with allure.step("Проверка ответа на создание справочника"):
            with pytest.raises(HTTPError, match=str(status)):
                assert create_dict_gen.try_create_dict(dict_body=custom_attr).status == status

    @allure.story("Невозможно создать справочник с dictValueTypeId пустым или отличным от строки с числом от 0 до 6 "
                  "включительно.")
    @allure.title("Попытаться создать справочники с недопустимыми valuetype, проверить, что недопустимо")
    @pytest.mark.parametrize('value_type,status', [("", 400),
                                                   ("8", 400),
                                                   ("-1", 400),
                                                   ("hellow", 400)])
    def test_create_custom_attr_type_negative(self, super_user, create_dict_gen, value_type, status):
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id=value_type,
                values=[value])
        with allure.step("Проверка ответа на создание справочника"):
            with pytest.raises(HTTPError, match=str(status)):
                assert create_dict_gen.try_create_dict(dict_body=custom_attr).status == status

    @allure.story("При наличии у хотя бы одного из value непустого значения в dictValueDisplayName - он должен "
                  "присутствовать у всех value(иначе - невозможно создать)")
    @allure.title("Создать справочник с одним значением с заполненным отображаемым именем, а другим без")
    @allure.issue("DEV-7531")
    def test_create_custom_attr_not_all_values(self, super_user, create_dict_gen):
        dict_name = "ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Создание справочника valueDispayName не у всех значений"):
            value1 = dict_value_construct(dict_value="52",
                                          dict_value_display_name="Nizhniy_Novgorod")
            value2 = dict_value_construct(dict_value="77",
                                          dict_value_display_name="")
            custom_attr = dict_construct(dict_name=dict_name,
                                         dict_value_type_id="1",
                                         values=[value1, value2])
            with pytest.raises(HTTPError, match="400"):
                assert create_dict_gen.try_create_dict(dict_body=custom_attr)

    @allure.story("Невозможно сохранить справочник без value")
    @allure.title("Создать справочник без значений")
    def test_create_custom_attr_empty_value(self, super_user, create_dict_gen):
        dict_name = "ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Создание справочника с пустыми значениями"):
            custom_attr = dict_construct(dict_name=dict_name,
                                         dict_value_type_id="1",
                                         values=[])
        with allure.step("Проверка, что запрещено"):
            with pytest.raises(HTTPError, match="400"):
                assert create_dict_gen.try_create_dict(dict_body=custom_attr)

    @allure.story("Невозможно создать справочник с именем, которое уже присутствует в списке справочников")
    @allure.title("Создать справочник с неуникальным именем")
    @allure.issue("DEV-7535")
    def test_create_custom_attr_non_unique_name(self, super_user, create_dict_gen):
        dict_name = "ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Создание справочника"):
            value1 = dict_value_construct(dict_value="77",
                                          dict_value_display_name="")
            custom_attr1 = dict_construct(dict_name=dict_name,
                                          dict_value_type_id="1",
                                          values=[value1])
            create_resul1t = create_dict_gen.try_create_dict(dict_body=custom_attr1)
        with allure.step("Создание справочника с неуникальным именем"):
            value2 = dict_value_construct(dict_value="77",
                                          dict_value_display_name="")
            custom_attr2 = dict_construct(dict_name=dict_name,
                                          dict_value_type_id="1",
                                          values=[value2])
        with allure.step("Проверка, что запрещено создавать справочник с неуникальным именем"):
            with pytest.raises(HTTPError, match="400"):
                assert create_dict_gen.try_create_dict(dict_body=custom_attr2)

    @allure.story("Значения справочника, указанные при создании корректно считываются")
    @allure.title("Создать справочник, проверить, что создался с корректными значениями")
    @pytest.mark.parametrize('value_type,dict_value,exp_val', [("0", "2.5", 2.5),
                                                               ("1", "20", 20),
                                                               ("2", "adas", "adas"),
                                                               ("3", 1702501200, 1702501200),
                                                               ("4", "true", True),
                                                               ("5", 1702562264, 1702562264),
                                                               ("6", "04:03:04", 14584)
                                                               ])
    @pytest.mark.smoke
    def test_create_dict_values_correct(self, super_user, create_dict_gen,
                                        value_type, dict_value, exp_val):
        with allure.step("Создание справочника"):
            # ("7",
            #  "1000000000000000000000000000000000000000",
            #  1000000000000000000000000000000000000000)
            if value_type == "6":
                h, m, s = dict_value.split(":")
                dict_value = int(h) * 3600 + int(m) * 60 + int(s)
            value = dict_value_construct(dict_value=dict_value,
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id=value_type,
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info_up: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
            assert attr_info_up.values[0]["dictValue"] == exp_val

    @allure.story("Значения справочника, указанные при создании корректно считываются")
    @allure.issue("DEV-7671")
    @allure.title("Создать справочник с некорректными значениями, проверить, как считываются")
    @pytest.mark.parametrize('value_type,dict_value', [("0", "2,5"),
                                                       ("1", "lala"),
                                                       ("3", "2022-01-12-12"),
                                                       ("4", "истина"),
                                                       ("5", "2022-01-12-12 12:25:45.010"),
                                                       ("6", "12:25:45.010")
                                                       ])
    def test_create_dict_values_correct_neg(self, super_user, create_dict_gen,
                                            value_type, dict_value):
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value=dict_value,
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id=value_type,
                values=[value])
        with allure.step("Проверка, что создание справочника запрещено"):
            with pytest.raises(HTTPError, match="400"):
                assert create_dict_gen.try_create_dict(dict_body=custom_attr)
