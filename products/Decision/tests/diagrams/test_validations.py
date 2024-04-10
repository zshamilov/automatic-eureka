from json import loads
from datetime import datetime

import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import JsonGenerationDto, \
    JsonGenerationValidationDto, JsonGenerationResultValidationDto, \
    DiagramInOutParameterFullViewDto, JsonGenerationResultDto
from products.Decision.framework.steps.decision_steps_diagram_helpers import generate_json_from_variables
from products.Decision.framework.steps.decision_steps_validate_api import get_ee_calc_result
from products.Decision.utilities.custom_models import IntValueType, AttrInfo, VariableParams
from products.Decision.utilities.variable_constructors import validation_variable_construct


@allure.epic("Диаграммы")
@allure.feature("Интерфейс валидации в Expression Editor")
@pytest.mark.scenario("DEV-12242")
class TestEeValidation:

    @allure.story("Для заданной переменной примитивного типа возвращается корректный json")
    @allure.title("Создаем переменную определенного типа, смотрим, что тип значения переменной "
                  "в возвращенном json соответствует заданному")
    @pytest.mark.parametrize("decision_type, python_type, is_array",
                             [(IntValueType.int, int, False),
                              (IntValueType.str, str, False),
                              (IntValueType.date, str, False),
                              (IntValueType.bool, bool, False),
                              (IntValueType.dateTime, str, False),
                              (IntValueType.time, str, False),
                              (IntValueType.long, int, False),
                              (IntValueType.int, list, True)],
                             ids=['int', 'str',
                                  'date', 'bool', 'dateTime',
                                  'time', 'long', 'array'])
    @pytest.mark.smoke
    def test_validations_json_values_primitive_types(self, super_user, decision_type, python_type, is_array):
        with allure.step("Создание переменной с заданными параметрами и подготовка body"):
            var_name = 'test_var'
            test_variable = validation_variable_construct(variable_name=var_name, type_id=decision_type,
                                                          is_array=is_array)
            test_variable_construct = JsonGenerationDto.construct(jsonVariables=[test_variable])
        with allure.step("Отправка запроса на получения json c переменными"):
            json_response = generate_json_from_variables(super_user, test_variable_construct)
            variables_in_json = loads(str(JsonGenerationResultDto.construct(
                **json_response.body).json))
        with allure.step("Проверка, что возвращенный тип соответствует ожидаемому"):
            assert isinstance(variables_in_json[var_name], python_type)

    @allure.story("Для заданной переменной комплексного типа возвращается корректный json")
    @allure.title("Создаем переменную комплексного типа, смотрим, что формат переменной в возвращенном"
                  " json соответствует заданному")
    @pytest.mark.variable_data([VariableParams(varName="out_int", varType="out", varDataType=1),
                                VariableParams(varName="in_cmplx", varType="in", isComplex=True,
                                               isConst=False,
                                               cmplxAttrInfo=[AttrInfo(attrName="float_attr",
                                                                       intAttrType=IntValueType.float)])])
    @pytest.mark.smoke
    def test_validations_json_value_cmplx_type(self, super_user, diagram_constructor):
        with allure.step("Создание переменной с заданными параметрами и подготовка body"):
            input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
            cmplx_type_id = input_var.typeId
            var_name = 'in_cmplx'
            test_variable = validation_variable_construct(variable_name=var_name, type_id=cmplx_type_id,
                                                          is_complex=True)
            test_variable_construct = JsonGenerationDto.construct(jsonVariables=[test_variable])
        with allure.step("Отправка запроса на получения json c переменными"):
            json_response = generate_json_from_variables(super_user, test_variable_construct)
            variables_in_json = loads(str(JsonGenerationResultDto.construct(
                **json_response.body).json))
        with allure.step("Проверка, что возвращенный тип соответствует ожидаемому"):
            assert isinstance(variables_in_json[var_name], dict)

    @allure.story("Для типов дата, дата_время, время, возвращается корректный формат")
    @allure.title("Создаем переменную определенного типа, смотрим, что формат"
                  "значения переменной в возвращенном json соответствует заданному")
    @pytest.mark.parametrize("decision_type, pattern",
                             [(IntValueType.date, "%Y-%m-%d"),
                              (IntValueType.dateTime, "%Y-%m-%d %H:%M:%S.%f"),
                              (IntValueType.time, "%H:%M:%S.%f")],
                             ids=['date', 'datetime', 'time'])
    @pytest.mark.smoke
    def test_validations_json_datetime_patterns(self, super_user, decision_type, pattern):
        with allure.step("Создание переменной с заданными параметрами и подготовка body"):
            var_name = 'test_var'
            test_variable = validation_variable_construct(variable_name=var_name, type_id=decision_type)
            test_variable_construct = JsonGenerationDto.construct(jsonVariables=[test_variable])
            pattern_correct = False
        with allure.step("Отправка запроса на получения json c переменными"):
            json_response = generate_json_from_variables(super_user, test_variable_construct)
            variables_in_json = loads(str(JsonGenerationResultDto.construct(
                **json_response.body).json))
            input_string = variables_in_json[var_name]
        with allure.step("Проверка на соответствие заданному паттерну"):
            try:
                datetime.strptime(input_string, pattern)
                pattern_correct = True
            except ValueError:
                pattern_correct = False
            assert pattern_correct

    @allure.story("Для заданных входной и выходной переменной возвращается результат выражения в корректном формате")
    @allure.title("Создаем переменные определенного типа, смотрим, что значение результата выражения"
                  " соответствует заданному формату")
    @pytest.mark.parametrize("decision_type, python_type, is_array",
                             [(IntValueType.float, float, False),
                              (IntValueType.int, int, False),
                              (IntValueType.str, str, False),
                              (IntValueType.date, str, False),
                              (IntValueType.bool, bool, False),
                              (IntValueType.dateTime, str, False),
                              (IntValueType.time, str, False),
                              (IntValueType.long, int, False),
                              (IntValueType.int, list, True)],
                             ids=['float', 'int', 'str',
                                  'date', 'bool', 'dateTime',
                                  'time', 'long', 'array'])
    @pytest.mark.smoke
    def test_validations_expression_results_primitive_types(self, super_user, decision_type,
                                                            python_type, is_array):
        with allure.step("Создание входной и результирующей переменных с заданными параметрами и подготовка body"):
            expression_variable_name = 'in_var'
            result_expression_variable_name = 'res_var'
            expression_text = f'${expression_variable_name}'
            expression_variable = validation_variable_construct(variable_name=expression_variable_name,
                                                                type_id=decision_type,
                                                                is_array=is_array)
            result_expression_variable = validation_variable_construct(variable_name=result_expression_variable_name,
                                                                       type_id=decision_type,
                                                                       is_array=is_array)
            expression_variable_construct = \
                JsonGenerationDto.construct(jsonVariables=[expression_variable])
        with allure.step("Отправка запроса на получения json для выражения c переменными"):
            json_response = generate_json_from_variables(super_user, expression_variable_construct)
            json_for_expression = str(JsonGenerationResultDto.construct(
                **json_response.body).json)
        with allure.step("Отправка запроса на валидацию выражения"):
            ee_body_construct = JsonGenerationValidationDto.construct(expression=expression_text,
                                                                      json=json_for_expression,
                                                                      calculatedParameter=result_expression_variable,
                                                                      jsonVariables=[expression_variable],
                                                                      functionIds=[])
            expression_response = get_ee_calc_result(super_user, ee_body_construct)
            final_result_variable = loads(str(JsonGenerationResultValidationDto.construct(
                **expression_response.body).result))
        with allure.step("Проверка, что возвращенный тип соответствует ожидаемому и выражение успешно"):
            assert isinstance(final_result_variable[str(result_expression_variable_name)], python_type)
            assert expression_response.body["status"] == "SUCCESS"

    @allure.story("Для заданных входной и выходной комплексной переменной возвращается результат выражения в "
                  "корректном формате")
    @allure.title("Создаем переменные комплексного типа типа, смотрим, что значение результата выражения"
                  " соответствует заданному формату")
    @pytest.mark.variable_data([VariableParams(varName="out_int", varType="out", varDataType=1),
                                VariableParams(varName="in_cmplx", varType="in", isComplex=True,
                                               isConst=False,
                                               cmplxAttrInfo=[AttrInfo(attrName="float_attr",
                                                                       intAttrType=IntValueType.float)])])
    @pytest.mark.smoke
    def test_validations_expression_results_cmplx_type(self, super_user, diagram_constructor):
        with allure.step("Получение информации о предсозданной комплексной переменной"):
            input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
            cmplx_type_id = input_var.typeId
            expression_variable_name = 'in_cmplx'
            result_expression_variable_name = 'out_cmplx'
        with allure.step("Создание входной и результирующей переменных с заданными параметрами и подготовка body"):
            expression_variable = validation_variable_construct(variable_name=expression_variable_name,
                                                                type_id=cmplx_type_id,
                                                                is_complex=True)
            expression_text = f'${expression_variable_name}'
            result_expression_variable = validation_variable_construct(variable_name=result_expression_variable_name,
                                                                       type_id=cmplx_type_id,
                                                                       is_complex=True)
            expression_variable_construct = \
                JsonGenerationDto.construct(jsonVariables=[expression_variable])
        with allure.step("Отправка запроса на получения json для выражения c переменными"):
            json_response = generate_json_from_variables(super_user, expression_variable_construct)
            json_for_expression = str(JsonGenerationResultDto.construct(
                **json_response.body).json)
        with allure.step("Отправка запроса на валидацию выражения"):
            ee_body_construct = JsonGenerationValidationDto.construct(expression=expression_text,
                                                                      json=json_for_expression,
                                                                      calculatedParameter=result_expression_variable,
                                                                      jsonVariables=[expression_variable],
                                                                      functionIds=[])
            expression_response = get_ee_calc_result(super_user, ee_body_construct)
            final_result_variable = loads(str(JsonGenerationResultValidationDto.construct(
                **expression_response.body).result))
        with allure.step("Проверка, что возвращенный тип соответствует ожидаемому и выражение успешно"):
            assert isinstance(final_result_variable[str(result_expression_variable_name)], dict)
            assert expression_response.body["status"] == "SUCCESS"

    @allure.story("Несовпадающее по типу с результирующей переменной выражение невалидно")
    @allure.title("Создаем переменные несовпадающих типов, смотрим, что значение результата выражения неуспешно")
    @pytest.mark.parametrize("decision_in_type, decision_out_type, is_array",
                             [(IntValueType.float, IntValueType.date, False),
                              (IntValueType.int, IntValueType.dateTime, False),
                              (IntValueType.str, IntValueType.long, False),
                              (IntValueType.date, IntValueType.bool, False),
                              (IntValueType.bool, IntValueType.str, False),
                              (IntValueType.dateTime, IntValueType.long, False),
                              (IntValueType.time, IntValueType.int, False),
                              (IntValueType.long, IntValueType.date, False),
                              (IntValueType.int, IntValueType.date, True)],
                             ids=['float-int', 'int-str', 'str',
                                  'date', 'bool', 'dateTime',
                                  'time', 'long', 'array'])
    @pytest.mark.smoke
    def test_validations_expression_results_primitive_types(self, super_user, decision_in_type, decision_out_type,
                                                            is_array):
        with allure.step("Создание входной и результирующей переменных с заданными параметрами и подготовка body"):
            expression_variable_name = 'in_var'
            result_expression_variable_name = 'res_var'
            expression_text = f'${expression_variable_name}'
            expression_variable = validation_variable_construct(variable_name=expression_variable_name,
                                                                type_id=decision_in_type,
                                                                is_array=is_array)
            result_expression_variable = validation_variable_construct(variable_name=result_expression_variable_name,
                                                                       type_id=decision_out_type,
                                                                       is_array=is_array)
            expression_variable_construct = \
                JsonGenerationDto.construct(jsonVariables=[expression_variable])
        with allure.step("Отправка запроса на получения json для выражения c переменными"):
            json_response = generate_json_from_variables(super_user, expression_variable_construct)
            json_for_expression = str(JsonGenerationResultDto.construct(
                **json_response.body).json)
        with allure.step("Отправка запроса на валидацию вырежния"):
            ee_body_construct = JsonGenerationValidationDto.construct(expression=expression_text,
                                                                      json=json_for_expression,
                                                                      calculatedParameter=result_expression_variable,
                                                                      jsonVariables=[expression_variable],
                                                                      functionIds=[])
        with allure.step("Проверка, что выражение не прошло валидацию"):
            with pytest.raises(HTTPError):
                assert get_ee_calc_result(super_user, ee_body_construct).body["status"] == "FAILED"
