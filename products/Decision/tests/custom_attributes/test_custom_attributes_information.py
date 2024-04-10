import datetime

import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import ResponseDto, \
    CustomAttributeDictionaryValueFullView, CustomAttributeDictionaryShortInfo
from products.Decision.framework.steps.decision_steps_custom_attr_dict import get_custom_attribute_values, \
    get_custom_attributes_by_types, custom_attributes_list
from products.Decision.framework.steps.decision_steps_diagram import validate_diagram
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct


@allure.epic("Справочники")
@allure.feature("Информация о справочниках")
@pytest.mark.scenario("DEV-5628")
class TestCustomAttributesInformation:

    # @allure.story("По справочникам возможно получить список диаграмм со справочником /custom-attribute-dict/{"
    #               "dictId}/diagrams")
    # @allure.issue("DEV-7757")
    # @allure.title("Получить список диаграмм, в которых используется справочник")
    # def test_find_diagrams_with_custom_attr(self, super_user, simple_diagram_dict_attr):
    #     dict_found_in_diagram = False
    #     dict_id = simple_diagram_dict_attr["dict_id"]
    #     saved_version_id = simple_diagram_dict_attr["saved_version_id"]
    #     diagram_list = []
    #     with allure.step("Получение списка диаграмм, в которых присутствует справочник"):
    #         for diagram in get_custom_attribute_diagrams(super_user, dict_id=dict_id).body:
    #             diagram_list.append(CustomAttributeDictionaryToDiagramFullView(**diagram))
    #     with allure.step("Проверка, что диаграммы найдены"):
    #         for diagram in diagram_list:
    #             if diagram.diagramVersionId == saved_version_id:
    #                 dict_found_in_diagram = True
    #         assert len(diagram_list) != 0

    @allure.story("Диаграмма со справочником в переменной проходит валидацию")
    @allure.title("Для диаграммы с переменной-справочником запустить валидацию")
    @allure.issue("DEV-7671")
    @pytest.mark.smoke
    def test_diagram_with_custom_attr_valid(self, super_user, simple_diagram_dict_attr):
        with allure.step("Получение версии диаграммы с переменной-справочником"):
            saved_version_id = simple_diagram_dict_attr["saved_version_id"]
        with allure.step("Запрос на валидацию данной диаграммы"):
            valid_resp: ResponseDto = ResponseDto.construct(
                **validate_diagram(super_user, version_id=saved_version_id).body)
        assert valid_resp.httpCode == 200

    @allure.story("По идентификатору справочника есть вся информация о значениях справочника")
    @allure.title("Получить значения справочника")
    @pytest.mark.smoke
    def test_get_dict_values(self, super_user, create_dict_gen):
        value_found = False
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="24",
                                         dict_value_display_name="age")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение списка значений справочника"):
            value_list = []
            for val in get_custom_attribute_values(super_user, dict_id=create_result.uuid).body:
                value_list.append(CustomAttributeDictionaryValueFullView.construct(**val))
            for val in value_list:
                if val.dictExpression == "24" and val.dictValueDisplayName == "age" \
                        and val.dictValue == 24:
                    value_found = True
        with allure.step("Проверка, что найденные значения корректны"):
            assert value_found and len(value_list) == 1

    @allure.story("В списке справочников по типу присутствуют только справочники с типом из запроса")
    @allure.title("Получить справочники по заданному в запросе типу")
    @pytest.mark.parametrize('value_type,dict_value', [("0", "2.5"),
                                                       ("1", "20"),
                                                       ("2", "adas"),
                                                       ("3", "2022-01-12"),
                                                       ("4", "true"),
                                                       ("5", "2022-01-12 12:25:45.010"),
                                                       ("6", "12:25:45"),
                                                       ("7",
                                                        "100000")
                                                       ])
    @pytest.mark.smoke
    def test_get_dicts_by_value_types(self, super_user, create_dict_gen,
                                      value_type, dict_value):
        with allure.step("Создание справочника"):
            if value_type == "3":
                dict_value = int(datetime.datetime.strptime(dict_value, "%Y-%m-%d").timestamp())
            if value_type == "5":
                dict_value = int(datetime.datetime.strptime(dict_value, "%Y-%m-%d %H:%M:%S.%f").timestamp())
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
        with allure.step("Получение списка справочников по заданному типу значения"):
            dict_list = []
            for d in get_custom_attributes_by_types(super_user, dict_value_type_id=value_type).body:
                dict_list.append(CustomAttributeDictionaryShortInfo.construct(**d))
        with allure.step("Проверка, что у всех справочников в списке тип соответствует заданному в запросе"):
            assert all(d.dictValueTypeId == value_type for d in dict_list)

    @allure.story("Вся информация о справочниках без значений есть в списке справочников")
    @allure.title("Получить список справочников, проверить поля")
    @pytest.mark.smoke
    def test_custom_attr_list(self, super_user, create_dict_gen):
        with allure.step("Получение списка справочников"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_string(),
                dict_value_type_id="1",
                values=[value])
            create_dict_gen.create_dict(custom_attr)
            custom_attrs_list = []
            for custom_attribute in custom_attributes_list(super_user).body["content"]:
                custom_attrs_list.append(
                    CustomAttributeDictionaryShortInfo.construct(**custom_attribute))
        with allure.step("Проверка, что у справочников в списке возвращается корректная информация"):
            attrs_contain_req_fields = next((attr for attr in custom_attrs_list if
                                             attr.dictValueTypeId is not None
                                             and attr.changeDt is not None
                                             and attr.createDt is not None
                                             and attr.dictName is not None
                                             and attr.id is not None
                                             and attr.createByUser is not None
                                             and attr.lastChangeByUser is not None), True)
            assert attrs_contain_req_fields
