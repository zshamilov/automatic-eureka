import time

import allure
import pytest

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.utilities.custom_models import VariableParams, IntValueType

from products.Decision.runtime_tests.runtime_fixtures.commhub_write_fixtures import *


@allure.epic("Узел записи в CommHub")
@allure.feature("Узел записи в CommHub")
class TestRuntimeCommHubWrite:

    @allure.story("Диаграмма с узлом записи в CommHub отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом записи в CommHub, проверить, что готова к развертыванию")
    @pytest.mark.commhub
    @pytest.mark.variable_data(
        [VariableParams(varName="in_comm_address", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_channel", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_control_group", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_comm_ignore_hours", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_comm_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_client_id_type", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_priority", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_task", varType="out", isComplex=True, isArray=False, isConst=False,
                        varValue="Task_Root")])
    @pytest.mark.nodes(["коммуникация", "запись commhub"])
    def test_submit_commhub_without_filters(self, super_user, commhub_write):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = commhub_write["diagram_data"].diagramId
            diagram_name = commhub_write["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Отправить сообщение в диаграмму с узлом записи в CommHub")
    @allure.title(
        "Отправить сообщение в диаграмму с узлом записи в CommHub, проверить, что отработала успешно")
    @pytest.mark.commhub
    @pytest.mark.variable_data(
        [VariableParams(varName="in_comm_address", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_channel", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_control_group", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_comm_ignore_hours", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_comm_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_client_id_type", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_comm_priority", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_task", varType="out", isComplex=True, isArray=False, isConst=False,
                        varValue="Task_Root")])
    @pytest.mark.nodes(["коммуникация", "запись commhub"])
    def test_send_message_commhub_write(self, super_user, integration_user,
                                        commhub_write, get_env,
                                        deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = commhub_write["diagram_data"].diagramId
            diagram_name = commhub_write["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
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
            address = f"{generate_string(6)}@mail.com"
            channel = "SMS"
            control_group = True
            ignore_hours = True
            client_id = generate_string(6)
            client_id_type = generate_string(6)
            priority = 'LOW'
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_comm_address": address,
                      "in_comm_channel": channel,
                      "in_comm_control_group": control_group,
                      "in_comm_ignore_hours": ignore_hours,
                      "in_comm_client_id": client_id,
                      "in_comm_client_id_type": client_id_type,
                      "in_comm_priority": priority},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["out_task"] is not None and \
                   message_response["diagram_execute_status"] == "1"
