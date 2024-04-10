import time
import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.tarantool_read_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, AttrInfo


@allure.epic("Тарантул Чтение")
@allure.feature("Тарантул Чтение")
class TestRuntimeTarantoolRead:
    @allure.story("Диаграмма с узлом чтение Tarantool поиск по индексу отправляется на развёртывание")
    @allure.title("Развернуть диаграмму с узлом чтение Tarantool поиск по индексу, проверить, что готова к "
                  "развёртыванию")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("ALL")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_long", varType="out", varDataType=IntValueType.long.value, isConst=False,
                        varValue="out_long"),
         VariableParams(varName="out_str", varType="out", varDataType=IntValueType.str.value, isConst=False,
                        varValue="out_str"),
         VariableParams(varName="in_long_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_long_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["чтение тарантул"])
    def test_submit_tarantool_read_tdg_index(self, super_user, tarantool_read_index_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_read_index_saved["diagram_data"].diagramId
            diagram_name = tarantool_read_index_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Диаграмма с узлом чтение Tarantool вызов функции отправляется на развёртывание")
    @allure.title("Развернуть диаграмму с узлом чтение Tarantool вызов функции, проверить, что готова к "
                  "развёртыванию")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.search_type("LUA_FUNCTION_SEARCH")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_int"),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение тарантул"])
    def test_submit_tarantool_read_tdg_function(self, super_user, tarantool_read_function_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_read_function_saved["diagram_data"].diagramId
            diagram_name = tarantool_read_function_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Диаграмма с узлом чтение Tarantool чтение массива отправляется на развёртывание")
    @allure.title("Развернуть диаграмму с узлом чтение Tarantool чтение массива, проверить, что готова к "
                  "развёртыванию")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("OfferLower")
    @pytest.mark.index_type("ALL")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_long", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_cmplx", varType="in_out", isArray=True, isComplex=True,
                        isConst=False,
                        cmplxAttrInfo=[AttrInfo(attrName="long_attr1",
                                                intAttrType=IntValueType.long),
                                       AttrInfo(attrName="long_attr2",
                                                intAttrType=IntValueType.long),
                                       AttrInfo(attrName="long_attr3",
                                                intAttrType=IntValueType.long)])])
    @pytest.mark.nodes(["чтение тарантул"])
    def test_submit_tarantool_read_tdg_array(self, super_user, tarantool_read_array_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_read_array_saved["diagram_data"].diagramId
            diagram_name = tarantool_read_array_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("В диаграмму с узлом чтение Tarantool поиск по индексу можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом чтение Tarantool поиск по индексу, "
                  "проверить, что ответ корректный")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("ALL")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_long", varType="out", varDataType=IntValueType.long.value, isConst=False,
                        varValue="out_long"),
         VariableParams(varName="out_str", varType="out", varDataType=IntValueType.str.value, isConst=False,
                        varValue="out_str"),
         VariableParams(varName="in_long_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_long_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["чтение тарантул"])
    def test_send_message_tarantool_read_tdg_index(self, super_user, integration_user, tarantool_read_index_saved,
                                                   get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_read_index_saved["diagram_data"].diagramId
            diagram_name = tarantool_read_index_saved["diagram_name"]
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
                body={"in_long_1": 21, "in_long_2": 2},
            ).body
        with allure.step("Статус отработки диаграммы 1 - без ошибок, и из Tarantool были прочитаны две переменные: "
                         "типа long и string"):
            assert message_response["out_long"] == 1 and message_response["out_str"] == "some_string" and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("В диаграмму с узлом чтение Tarantool вызов функции можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом чтение Tarantool вызов функции, "
                  "проверить, что ответ корректный")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.search_type("LUA_FUNCTION_SEARCH")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_int"),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение тарантул"])
    def test_send_message_tarantool_read_tdg_fun(self, super_user, integration_user, tarantool_read_function_saved,
                                                 get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_read_function_saved["diagram_data"].diagramId
            diagram_name = tarantool_read_function_saved["diagram_name"]
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
                body={"in_int_1": 2, "in_int_2": 3},
            ).body
        with allure.step("Статус отработки диаграммы 1 - без ошибок и в выходной переменной сумма двух аргументов "
                         "функции"):
            assert message_response["out_int"] == 5 and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("В диаграмму с узлом чтение Tarantool чтение массива можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом чтение Tarantool чтение массива, "
                  "проверить, что ответ корректный")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("OfferLower")
    @pytest.mark.index_type("ALL")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_long", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_cmplx", varType="in_out", isArray=True, isComplex=True,
                        isConst=False,
                        cmplxAttrInfo=[AttrInfo(attrName="long_attr1",
                                                intAttrType=IntValueType.long),
                                       AttrInfo(attrName="long_attr2",
                                                intAttrType=IntValueType.long),
                                       AttrInfo(attrName="long_attr3",
                                                intAttrType=IntValueType.long)])])
    @pytest.mark.nodes(["чтение тарантул"])
    def test_send_message_tarantool_read_tdg_array(self, super_user, integration_user, tarantool_read_array_saved,
                                                   get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = tarantool_read_array_saved["diagram_data"].diagramId
            diagram_name = tarantool_read_array_saved["diagram_name"]
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
                body={
                    "in_cmplx":
                        [{
                            "long_attr1": 2,
                            "long_attr2": 1,
                            "long_attr3": 56
                        },
                            {
                                "long_attr1": 22,
                                "long_attr2": 1,
                                "long_attr3": 56
                            }
                        ],
                    "in_long": 1
                }
            ).body
        with allure.step("Проверка, что статус отработки диаграммы 1 - без ошибок и вернула обогащенный массив "
                         "пользовательского типа"):
            assert message_response["in_cmplx"] == [{'long_attr1': 2, 'long_attr2': None, 'long_attr3': 56},
                                                    {'long_attr1': 22, 'long_attr2': 33, 'long_attr3': 56}] and \
                   message_response["diagram_execute_status"] == "1"
