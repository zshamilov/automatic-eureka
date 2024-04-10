import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.tarantool_insert_fixtures import *
from products.Decision.utilities.custom_models import VariableParams


@allure.epic("Тарантул Запись")
@allure.feature("Тарантул Запись")
class TestRuntimeTarantoolInsert:

    @allure.story("Диаграмма с узлом тарантул запись отправляется на развёртывание")
    @allure.title("Отправить диаграмму с узлом тарантул-обновление на развёртывание, проверить, что готова к "
                  "развёртыванию")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    def test_submit_tarantool_ins_tdg_update(self, super_user, tarantool_insert_update_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_insert_update_saved["diagram_data"].diagramId
            diagram_name = tarantool_insert_update_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Диаграмма с узлом тарантул запись отправляется на развёртывание")
    @allure.title("Отправить сообщение в диаграмму с узлом тарантул-обновление, проверить, что диаграмма отрабатывает")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    def test_send_message_tarantool_ins_tdg_update(self, super_user, integration_user,
                                                   tarantool_insert_update_saved,
                                                   get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_insert_update_saved["diagram_data"].diagramId
            diagram_name = tarantool_insert_update_saved["diagram_name"]
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
                body={"in_out_int": 21, "in_int_1": 2, "in_int_2": 1},
            ).body
        with allure.step("Статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_execute_status"] == "1"

    @allure.story("Диаграмма с узлом тарантул запись отправляется на развёртывание")
    @allure.title("Отправить сообщение в  диаграмму с узлом тарантул-вставка, проверить, что диаграмма отрабатывает")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_str", varType="in", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["запись тарантул"])
    def test_send_message_tarantool_ins_tdg_insert(self, super_user, integration_user,
                                                   tarantool_insert_insert_saved,
                                                   get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_insert_insert_saved["diagram_data"].diagramId
            diagram_name = tarantool_insert_insert_saved["diagram_name"]
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
                body={"in_out_int": 21, "in_int_1": 2, "in_int_2": 1, "in_str": "some_string"},
            ).body
        with allure.step("Статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_execute_status"] == "1"

    @allure.story("Диаграмма с узлом тарантул запись отправляется на развёртывание")
    @allure.title("Отправить сообщение в диаграмму с узлом тарантул-вставка и обновление, проверить, что диаграмма "
                  "отрабатывает")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("PRIMARY")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_str", varType="in", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["запись тарантул"])
    def test_send_message_tarantool_ins_tdg_upsert(self, super_user, integration_user,
                                                   tarantool_insert_upsert_saved,
                                                   get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_insert_upsert_saved["diagram_data"].diagramId
            diagram_name = tarantool_insert_upsert_saved["diagram_name"]
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
                body={"in_out_int": 21, "in_int_1": 2, "in_int_2": 1, "in_str": "some_string"},
            ).body
        with allure.step("Статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_execute_status"] == "1"

    @allure.story(
        "Диаграмма с узлом тарантул запись, режим - 'обновление' и константой отправляется на развёртывание,"
    )
    @allure.title(
        "Обновить узел записи указав в маппинге константы и выбрать режим - 'обновление'"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_update_constant(self, super_user, integration_user,
                                                  tarantool_constant_insert_update_saved,
                                                  get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_constant_insert_update_saved["diagram_data"].diagramId
            diagram_name = tarantool_constant_insert_update_saved["diagram_name"]
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
                body={"in_out_int": 21},
            ).body
        with allure.step("Статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_execute_status"] == "1"

    @allure.story(
        "Диаграмма с узлом тарантул запись, режим - 'Вставка' и константой отправляется на развёртывание,"
    )
    @allure.title(
        "Обновить узел записи указав в маппинге константы и выбрать режим - 'Вставка'"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("TEST_PRIMITIVE_ALL_TYPES")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_all_node_insert_constant(self, super_user, integration_user,
                                                      tarantool_constant_insert_insert_saved,
                                                      get_env, deploy_diagrams_gen):
        with allure.step("Получение информации"):
            diagram_id = tarantool_constant_insert_insert_saved["diagram_data"].diagramId
            diagram_name = tarantool_constant_insert_insert_saved["diagram_name"]

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
                body={"in_out_int": 21},
            ).body
        with allure.step("Статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_execute_status"] == "1"

    @allure.story(
        "Диаграмма с узлом тарантул с режимом - 'Вставка и обновление' и константой отправляется на развёртывание"
    )
    @allure.title(
        "Обновить узел записи указав в маппинге константы и с режимом - 'Вставка и обновление'"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("PRIMARY")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_upsert_constant(self, super_user, integration_user,
                                                  tarantool_constant_insert_upsert_saved,
                                                  get_env, deploy_diagrams_gen):
        with allure.step("Получение информации"):
            diagram_id = tarantool_constant_insert_upsert_saved["diagram_data"].diagramId
            diagram_name = tarantool_constant_insert_upsert_saved["diagram_name"]

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
                body={"in_out_int": 21},
            ).body
        with allure.step("Статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["diagram_execute_status"] == "1"
