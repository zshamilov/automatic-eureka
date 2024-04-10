import uuid

import allure
import pytest

from products.Decision.framework.model import ResponseDto, DiagramViewDto
from products.Decision.framework.steps.decision_steps_diagram import update_diagram_parameters, get_diagram_by_version, \
    validate_diagram
from products.Decision.framework.steps.decision_steps_nodes import create_node, create_link
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.node_cunstructors import variables_for_node, node_construct, link_construct
from products.Decision.utilities.variable_constructors import variable_construct


@allure.epic("Диаграммы")
@allure.feature("Аварийный ответ")
@pytest.mark.scenario("DEV-518")
class TestDiagramsEmergencyResponse:

    @allure.story("В put /parameters в аттрибут defaultValue: должно находиться значение с типом совпадающим с typeId")
    @allure.title("Создать переменную с defult value не совпадающим по типу с значением переменной, провалидировать")
    @pytest.mark.skip("obsolete")
    def test_validate_diagram_vars_default_val(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание данных параметров"):
            rand_string_param_name = generate_diagram_name_description(8, 1)["rand_name"]
            parameter_version_id2 = uuid.uuid4()
        with allure.step("Обновить параметров на переменную с несовпадающим по типу defaultValue"):
            params_response = update_diagram_parameters(super_user,
                                                        temp_version_id,
                                                        [variable_construct(),
                                                         variable_construct(array_flag=False,
                                                                            complex_flag=False,
                                                                            default_value="this is not int",
                                                                            is_execute_status=None,
                                                                            order_num=0,
                                                                            param_name=rand_string_param_name,
                                                                            parameter_type="in_out",
                                                                            parameter_version_id=parameter_version_id2,
                                                                            type_id=1
                                                                            )])
            update_response: ResponseDto = params_response.body
            start_variables = variables_for_node(node_type="start",
                                                 is_arr=False,
                                                 is_compl=False,
                                                 name=rand_string_param_name,
                                                 type_id=1,
                                                 vers_id=parameter_version_id2
                                                 )
            finish_variables = variables_for_node(node_type="finish",
                                                  is_arr=False,
                                                  is_compl=False,
                                                  name=rand_string_param_name,
                                                  type_id=1,
                                                  vers_id=parameter_version_id2
                                                  )
            node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
            node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id, [finish_variables])
            node_start_response = create_node(super_user, node_start_raw)
            node_start: ResponseDto = node_start_response.body
            node_end_response = create_node(super_user, node_finish_raw)
            node_end: ResponseDto = node_end_response.body
            link_s_f = link_construct(temp_version_id, node_start["uuid"], node_end["uuid"])
            link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
        with allure.step("Поиск диаграммы по айди версии"):
            get_diagram_by_version_response = get_diagram_by_version(super_user, temp_version_id)
            diagram: DiagramViewDto = get_diagram_by_version_response.body
        with allure.step("Запрос на валидацию данной диаграммы"):
            valid_resp: ResponseDto = ResponseDto.construct(
                **validate_diagram(super_user, version_id=temp_version_id).body)
        with allure.step("Проверка, что валидация не прошла, так как defaultValue не совпадает с типом переменной"):
            assert valid_resp.httpCode == 422

    @allure.story("В put /parameters в аттрибут defaultValue: может передаваться Expression значение с типом "
                  "совпадающим с typeId")
    @allure.title("Создать переменную с defult value expression не совпадающим по типу с значением переменной, "
                  "провалидировать")
    @pytest.mark.skip("obsolete")
    def test_validate_diagram_vars_default_val_exp(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание данных параметров"):
            rand_string_param_name = generate_diagram_name_description(8, 1)["rand_name"]
            parameter_version_id2 = uuid.uuid4()
        with allure.step("Обновить параметров на переменную с несовпадающим по типу defaultValue expression"):
            params_response = update_diagram_parameters(super_user,
                                                        temp_version_id,
                                                        [variable_construct(),
                                                         variable_construct(array_flag=False,
                                                                            complex_flag=False,
                                                                            default_value="currentDate()",
                                                                            is_execute_status=None,
                                                                            order_num=0,
                                                                            param_name=rand_string_param_name,
                                                                            parameter_type="in_out",
                                                                            parameter_version_id=parameter_version_id2,
                                                                            type_id=1
                                                                            )])
            update_response: ResponseDto = params_response.body
            start_variables = variables_for_node(node_type="start",
                                                 is_arr=False,
                                                 is_compl=False,
                                                 name=rand_string_param_name,
                                                 type_id=1,
                                                 vers_id=parameter_version_id2
                                                 )
            finish_variables = variables_for_node(node_type="finish",
                                                  is_arr=False,
                                                  is_compl=False,
                                                  name=rand_string_param_name,
                                                  type_id=1,
                                                  vers_id=parameter_version_id2
                                                  )
            node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
            node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id, [finish_variables])
            node_start_response = create_node(super_user, node_start_raw)
            node_start: ResponseDto = node_start_response.body
            node_end_response = create_node(super_user, node_finish_raw)
            node_end: ResponseDto = node_end_response.body
            link_s_f = link_construct(temp_version_id, node_start["uuid"], node_end["uuid"])
            link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
        with allure.step("Поиск диаграммы по айди версии"):
            get_diagram_by_version_response = get_diagram_by_version(super_user, temp_version_id)
            diagram: DiagramViewDto = get_diagram_by_version_response.body
        with allure.step("Запрос на валидацию данной диаграммы"):
            valid_resp: ResponseDto = ResponseDto.construct(
                **validate_diagram(super_user, version_id=temp_version_id).body)
        with allure.step("Проверка, что валидация не прошла, так как defaultValue не совпадает с типом переменной"):
            assert valid_resp.httpCode == 422
