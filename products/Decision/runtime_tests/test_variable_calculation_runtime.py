import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, \
    find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.var_calc_fixtures import *
from products.Decision.utilities.custom_models import IntValueType, VariableParams


@allure.epic("Расчёт переменных")
@allure.feature("Расчёт переменных")
class TestRuntimeVarCalc:
    @allure.story("Диаграмма с узлом расчёта переменных отправляется на развёртку")
    @allure.title("Создать диаграмму, отправить на развертывание, проверить, что успешно")
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_var", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    def test_submit_diagram_var_calc(self, super_user,
                                     diagram_calc_prim_v):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_calc_prim_v["diagram_data"].diagramId
            diagram_name = diagram_calc_prim_v["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("В диаграмму с узлом расчёта переменных возможно отправить сообщение")
    @allure.title("Создать диаграмму, отправить на развертывание,развернуть, отправить сообщение")
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_var", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    def test_send_message_diagram_var_calc(self, super_user,
                                           integration_user,
                                           diagram_calc_prim_v,
                                           get_env,
                                           deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_calc_prim_v["diagram_data"].diagramId
            diagram_name = diagram_calc_prim_v["diagram_name"]
            diagram_param_in: DiagramInOutParameterFullViewDto = diagram_calc_prim_v["in_param"]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_calc_prim_v["out_param"]
            expected_calc_res = diagram_calc_prim_v["calc_val"]
        with allure.step("Отправка диаграммы на сабмит"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы"):
            env_id = get_env.get_env_id("default_dev")
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{diagram_param_in.parameterName}": 21},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param_out.parameterName}"] == expected_calc_res and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("Диаграмма с расчетом новой переменной и пользовательской функцией корректно отрабатывает")
    @allure.title("Создать диаграмму, отправить на развертывание,развернуть, отправить сообщение")
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_var", varType="out", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["расчет переменной"])
    def test_send_message_diagram_var_calc_func(self, super_user, integration_user,
                                                diagram_calc_func, get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_calc_func["diagram_id"]
            diagram_name = diagram_calc_func["diagram_name"]
            diagram_param_in = diagram_calc_func["in_param"]
            diagram_param_out = diagram_calc_func["out_param"]
            message_value = 21
            expected_calc_res = "zdarova " + str(message_value)
        with allure.step("Отправка диаграммы на сабмит"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы"):
            env_id = get_env.get_env_id("default_dev")
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{diagram_param_in.parameterName}": message_value},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param_out.parameterName}"] == expected_calc_res and \
                   message_response["diagram_execute_status"] == "1"
