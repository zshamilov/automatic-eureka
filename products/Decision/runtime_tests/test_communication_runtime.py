import time

import allure
import pytest

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message

from products.Decision.runtime_tests.runtime_fixtures.communication_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Узел коммуникация")
@allure.feature("Узел коммуникация")
class TestRuntimeCommunication:
    @allure.story("Диаграмма с узлом коммуникации с ручным вводом и груви-кодом отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом коммуникации с ручным вводом и груви-кодом, проверить, что готова к развертыванию")
    @pytest.mark.nodes(["коммуникация"])
    def test_submit_comm_groovy(self, super_user, communication_user_input_diagram_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_user_input_diagram_saved["diagram_data"].diagramId
            diagram_name = communication_user_input_diagram_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Диаграмма с узлом коммуникации с элементом диаграммы и груви-кодом отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом коммуникации с элементом диаграммы и груви-кодом, проверить, что готова к "
        "развертыванию")
    @pytest.mark.nodes(["коммуникация"])
    def test_submit_comm_diagram_elem_groovy(self, super_user, communication_diagram_element_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_diagram_element_saved["diagram_data"].diagramId
            diagram_name = communication_diagram_element_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Диаграмма с узлом коммуникации со справочником и груви-кодом отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом коммуникации со справочником и груви-кодом, проверить, что готова к развертыванию")
    @pytest.mark.nodes(["коммуникация"])
    def test_submit_comm_dict_groovy(self, super_user, communication_dict_diagram_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_dict_diagram_saved["diagram_data"].diagramId
            diagram_name = communication_dict_diagram_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Диаграмма с узлом коммуникации с переменной в узле и груви-кодом отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом коммуникации с переменной в узле и груви-кодом, проверить, что готова к "
        "развертыванию")
    @pytest.mark.nodes(["коммуникация"])
    def test_submit_comm_node_var_groovy(self, super_user, communication_node_var_diagram_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_node_var_diagram_saved["diagram_data"].diagramId
            diagram_name = communication_node_var_diagram_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("В диаграмму с узлом коммуникации с ручным вводом и груви-кодом можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом коммуникации с ручным вводом и груви-кодом, проверить, "
                  "что ответ корректный")
    @pytest.mark.nodes(["коммуникация"])
    def test_send_message_comm_groovy(self, super_user, integration_user,
                                      communication_user_input_diagram_saved, get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_user_input_diagram_saved["diagram_data"].diagramId
            diagram_name = communication_user_input_diagram_saved["diagram_name"]
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
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_int_v": 21},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["out_int_v"] == 1 and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("В диаграмму с узлом коммуникации с ручным вводом и груви-кодом можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом коммуникации с ручным вводом и груви-кодом, проверить, "
                  "что ответ корректный")
    @pytest.mark.nodes(["коммуникация"])
    def test_send_message_comm_diagram_elem_groovy(self, super_user, integration_user,
                                                   communication_diagram_element_saved, get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_diagram_element_saved["diagram_data"].diagramId
            diagram_name = communication_diagram_element_saved["diagram_name"]
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
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_int_v": 21},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["out_int_v"] == 1 and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("В диаграмму с узлом коммуникации со справочником и груви-кодом можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом коммуникации со справочником и груви-кодом с ручным вводом, "
                  "проверить,"
                  "что ответ корректный")
    @pytest.mark.nodes(["коммуникация"])
    def test_send_message_comm_dict_groovy(self, super_user, integration_user,
                                           communication_dict_diagram_saved, get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_dict_diagram_saved["diagram_data"].diagramId
            diagram_name = communication_dict_diagram_saved["diagram_name"]
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
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_int_v": 21},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["out_int_v"] == 1 and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("В диаграмму с узлом коммуникации с переменной в узле и груви-кодом можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом коммуникации с переменной в узле и груви-кодом, проверить, "
                  "что ответ корректный")
    @pytest.mark.nodes(["коммуникация"])
    def test_send_message_comm_node_var_groovy(self, super_user, integration_user,
                                               communication_node_var_diagram_saved, get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = communication_node_var_diagram_saved["diagram_data"].diagramId
            diagram_name = communication_node_var_diagram_saved["diagram_name"]
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
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_int_v": 21},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["out_int_v"] == 1 and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("Диаграмма с узлом коммуникации с константами отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом коммуникации с константами, проверить, что готова к развертыванию")
    @pytest.mark.variable_data(
        [VariableParams(varName="out1", varType="out", varDataType=IntValueType.bool.value),
         VariableParams(varName="out2", varType="out", varDataType=IntValueType.date.value),
         VariableParams(varName="out3", varType="out", varDataType=IntValueType.time.value),
         VariableParams(varName="out4", varType="out", varDataType=IntValueType.dateTime.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["коммуникация"])
    def test_submit_comm_constant(self, super_user, saved_communication_consts_diagram_empty_node):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = saved_communication_consts_diagram_empty_node["diagram_data"].diagramId
            diagram_name = saved_communication_consts_diagram_empty_node["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("В диаграмму с узлом коммуникации с константой можно отправить сообщение")
    @allure.title(
        "Отправить сообщение в диаграмму с узлом коммуникации с константой, проверить, "
        "что ответ корректный")
    @pytest.mark.variable_data(
        [VariableParams(varName="out1", varType="out", varDataType=IntValueType.bool.value),
         VariableParams(varName="out2", varType="out", varDataType=IntValueType.date.value),
         VariableParams(varName="out3", varType="out", varDataType=IntValueType.time.value),
         VariableParams(varName="out4", varType="out", varDataType=IntValueType.dateTime.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["коммуникация"])
    def test_send_message_comm_constant(self, super_user, integration_user,
                                        saved_communication_consts_diagram_empty_node,
                                        get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = saved_communication_consts_diagram_empty_node["diagram_data"].diagramId
            diagram_name = saved_communication_consts_diagram_empty_node["diagram_name"]
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
            time.sleep(20)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_int": 11},
            ).body
        with allure.step("Пришло правильное значение выходных переменных и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_execute_status"] == "1" and message_response["out1"] is True \
                   and message_response["out2"] == '2023-12-22' and message_response["out3"] == '01:01:01' \
                   and message_response["out4"] == '2023-12-22 01:01:01.434'
