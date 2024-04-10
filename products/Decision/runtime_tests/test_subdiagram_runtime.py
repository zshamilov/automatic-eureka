import time

import allure
import pytest

from products.Decision.framework.model import DeployConfigurationFullDto, DiagramInOutParameterFullViewDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, deploy_config, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.subdiagram_fixtures import diagram_with_subdiagram_in_subdiagram
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Поддиаграмма")
@allure.feature("Поддиаграмма")
class TestRuntimeSubdiagram:

    @allure.story("Диаграмма с узлом поддиаграммы разворачивается в простом сценарии")
    @allure.title("Развернуть диаграмму с простым узлом поддиаграммы, проверить, что развернулась")
    @allure.issue("DEV-17107")
    def test_submit_diagram_with_subdiagram_node_working(self, super_user,
                                                         diagram_subdiagram_working):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_subdiagram_working["outer_diagram_template"].diagramId
            diagram_name = diagram_subdiagram_working["outer_diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
            # submit_response = put_diagram_submit(super_user, version_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("В диаграмму с узлом поддиаграммы можно отправить сообщение в простом сценарии")
    @allure.title("Развернуть диаграмму с простым узлом поддиаграммы, проверить, что сообщение соответствует ожиданиям")
    def test_send_message_diagram_with_subdiagram_node_working(self, super_user,
                                                               integration_user,
                                                               diagram_subdiagram_submit_working,
                                                               deploy_diagrams_gen):
        env_id = diagram_subdiagram_submit_working["env_id"]
        deploy_id = diagram_subdiagram_submit_working["deploy_id"]
        diagram_id = diagram_subdiagram_submit_working["diagram_id"]
        diagram_name = diagram_subdiagram_submit_working["diagram_name"]
        diagram_param_in: DiagramInOutParameterFullViewDto = diagram_subdiagram_submit_working["diagram_param"]
        diagram_param_out: DiagramInOutParameterFullViewDto = diagram_subdiagram_submit_working["diagram_param"]
        in_message_value = 21
        with allure.step("Деплой подготовленной диаграммы"):
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получить настройки развёрнутого деплоя"):
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{diagram_param_in.parameterName}": in_message_value},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param_out.parameterName}"] == in_message_value and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("В диаграмму с узлом поддиаграммы который ссылается на диаграмму с поддиаграммой"
                  "можно отправить сообщение ")
    @allure.title("Развернуть диаграмму с узлом поддиаграммы который ссылается на диаграмму с поддиаграммой, "
                  "проверить, что сообщение соответствует ожиданиям")
    @pytest.mark.variable_data(
        [VariableParams(varName="diagram_variable", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="diagram_variable")])
    @pytest.mark.nodes(["поддиаграмма"])
    def test_send_message_diagram_with_subdiagram_in_subdiagram(self, super_user,
                                                                integration_user,
                                                                diagram_with_subdiagram_in_subdiagram,
                                                                get_env,
                                                                deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_with_subdiagram_in_subdiagram["main_diagram_id"]
            diagram_name = diagram_with_subdiagram_in_subdiagram["diagram_name"]
            env_id = get_env.get_env_id("default_dev")
            in_message_value = 21
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы"):
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получить настройки развёрнутого деплоя"):
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"diagram_variable": in_message_value},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_variable"] == in_message_value and \
                   message_response["diagram_execute_status"] == "1"
