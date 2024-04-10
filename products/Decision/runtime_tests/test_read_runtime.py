import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.jdbc_read_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, AttrInfo


@allure.epic("Чтение данных")
@allure.feature("Чтение данных")
class TestRuntimeRead:
    @allure.story(
        "Диаграмма с узлом чтения отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом чтения на развёртование, проверить, что появилась в списке деплоев"
    )
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    def test_submit_diagram_with_read_node(self, super_user, diagram_read_2, save_diagrams_gen):
        node_read = diagram_read_2["node_read"]
        diagram_param = diagram_read_2["param"]
        temp_version_id = diagram_read_2["temp_version_id"]
        diagram_id = diagram_read_2["diagram_id"]
        columns: list[ColumnsDto] = diagram_read_2["table_columns"]
        provider: DataProviderGetFullView = diagram_read_2["data_provider"]
        table_name = diagram_read_2["table_name"]
        column_name = ""
        for column in columns:
            if column.dataType == "integer":
                column_name = column.columnName
                break

        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id="1",
                                               node_variable=column_name,
                                               is_jdbc_arr_key=False)
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=f"select {column_name}" + " \n" + f"from {table_name}",
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name],
                                                   plain_query=f"select {column_name} from {table_name}")
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            update_node(super_user, node_id=node_read.nodeId, body=update_body)
        with allure.step("Сохранение диаграммы"):
            diagram_name = "ag_diagram_read" + "_" + generate_string()
            diagram_description = 'diagram created in test'
            response_save: ResponseDto = save_diagrams_gen.save_diagram(diagram_id=diagram_id,
                                                                        temp_version_id=temp_version_id,
                                                                        new_diagram_name=diagram_name,
                                                                        diagram_description=diagram_description)
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
            # submit_response = put_diagram_submit(super_user, version_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "В диаграмму с узлом чтения возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом чтения, получить ответ"
    )
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    def test_send_message_diagram_with_read_node(self, super_user,
                                                 diagram_read_submit_2,
                                                 deploy_diagrams_gen,
                                                 integration_user):
        env_id = diagram_read_submit_2["env_id"]
        deploy_id = diagram_read_submit_2["deploy_id"]
        diagram_id = diagram_read_submit_2["diagram_id"]
        diagram_name = diagram_read_submit_2["diagram_name"]
        diagram_param = diagram_read_submit_2["diagram_param"]
        with allure.step("Деплой подготовленной диаграммы"):
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получить настройки развёрнутого деплоя"):
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутый диеплой"):
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{diagram_param.parameterName}": 21},
            ).body
        with allure.step("Пришло значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param.parameterName}"] is not None and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story("В диаграмму с узлом чтение данных с чтением массива можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом чтение данных с чтением массива, "
                  "проверить, что ответ корректный")
    @pytest.mark.scenario("DEV-3475")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="in_cmplx", varType="in_out", isArray=True, isComplex=True,
                        isConst=False,
                        cmplxAttrInfo=[AttrInfo(attrName="int_attr",
                                                intAttrType=IntValueType.int),
                                       AttrInfo(attrName="string_attr",
                                                intAttrType=IntValueType.str),
                                       AttrInfo(attrName="float_attr",
                                                intAttrType=IntValueType.float),
                                       AttrInfo(attrName="date_attr",
                                                intAttrType=IntValueType.date)])])
    @pytest.mark.nodes(["чтение"])
    def test_send_message_diagram_with_read_node_array(self, super_user, integration_user, read_array_saved,
                                                       get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = read_array_saved["diagram_data"].diagramId
            diagram_name = read_array_saved["diagram_name"]
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
                            "int_attr": 5,
                            "float_attr": 1.1,
                            "string_attr": "stroka",
                            "date_attr": "2023-01-01"
                        },
                            {
                                "int_attr": 5,
                                "float_attr": 2.2,
                                "string_attr": BasicPrimitiveValues.strBasic.value,
                                "date_attr": "2023-01-01"
                            }
                        ],
                    "in_int": BasicPrimitiveValues.intBasic.value
                }
            ).body
        with allure.step("Проверка, что статус отработки диаграммы 1 - без ошибок и вернула обогащенный массив "
                         "пользовательского типа"):
            assert message_response["in_cmplx"] == [{"float_attr": None,
                                                     "int_attr": 5,
                                                     "date_attr": None,
                                                     "string_attr": "stroka"},
                                                    {"float_attr": BasicPrimitiveValues.floatBasic.value,
                                                     "int_attr": 5,
                                                     "date_attr": BasicPrimitiveValues.dateBasic.value,
                                                     "string_attr": BasicPrimitiveValues.strBasic.value}] and \
                   message_response["diagram_execute_status"] == "1"
