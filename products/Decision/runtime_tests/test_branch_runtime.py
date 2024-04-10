import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.branch_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntNodeType, NodeFullInfo, IntValueType


@allure.epic("Ветвление")
@allure.feature("Ветвление")
class TestRuntimeBranch:
    @allure.story(
        "Диаграмма с узлом ветвления отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом ветвления на развёртование, проверить, что появилась в списке деплоев"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_submit_diagram_branch_node(self, super_user, diagram_branch_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_branch_saved["diagram_data"].diagramId
            diagram_name = diagram_branch_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "В диаграмму с узлом ветвления возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом ветвления, получить ответ"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_send_message_diagram_with_branch_node(self, super_user,
                                                   diagram_branch_saved,
                                                   get_env,
                                                   deploy_diagrams_gen,
                                                   integration_user):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_branch_saved["diagram_data"].diagramId
            diagram_name = diagram_branch_saved["diagram_name"]
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
        with allure.step("Отправка сообщения в развёрнутый диеплой"):
            first_cond_correct = False
            second_cond_correct = False
            time.sleep(10)
            message_response1 = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"in_out_var": 10},
            ).body
            message_response2 = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"in_out_var": 4},
            ).body
            if message_response1["in_out_var"] == 1 and \
                    message_response1["diagram_execute_status"] == "1":
                first_cond_correct = True
            if message_response2["in_out_var"] == 2 and \
                    message_response1["diagram_execute_status"] == "1":
                second_cond_correct = True
        with allure.step("Ответ на сообщение пошёл по нужной ветви для каждого сообщения"):
            assert first_cond_correct
            assert second_cond_correct
