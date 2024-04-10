import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.scorecard_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Рассчёт скоркарты")
@allure.feature("Рассчёт скоркарты")
class TestRuntimeScorecard:
    @allure.story(
        "Диаграмма с узлом рассчёта скоркарты отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом рассчёта скоркарты на развёртование, проверить, что появилась в списке деплоев"
    )
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_v", varType="in_out", varDataType=IntValueType.int.value),
         VariableParams(varName="score_v", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["скоркарта"])
    def test_submit_diagram_scorecard_node(self, super_user, diagram_scorecard):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_scorecard["diagram_data"].diagramId
            diagram_name = diagram_scorecard["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "В диаграмму с узлом рассчёта скоркарты возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом рассчёта скоркарты, получить ответ"
    )
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_v", varType="in_out", varDataType=IntValueType.int.value),
         VariableParams(varName="score_v", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["скоркарта"])
    def test_send_message_diagram_with_scorecard_node(self, super_user,
                                                      diagram_scorecard,
                                                      get_env,
                                                      deploy_diagrams_gen,
                                                      integration_user):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_scorecard["diagram_data"].diagramId
            diagram_name = diagram_scorecard["diagram_name"]
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
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_out_v": 10,
                      "score_v": 1}
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["in_out_v"] == 1 and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story(
        "В диаграмму с узлом рассчёта скоркарты с картой, загруженной из excel, возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом рассчёта скоркарты с картой, загруженной из excel, получить ответ"
    )
    @pytest.mark.variable_data(
        [VariableParams(varName="a", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="b", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["скоркарта"])
    def test_send_message_diagram_with_scorecard_node_excel(self, super_user,
                                                            diagram_scorecard_from_excel,
                                                            get_env,
                                                            deploy_diagrams_gen,
                                                            integration_user):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_scorecard_from_excel["diagram_data"].diagramId
            diagram_name = diagram_scorecard_from_excel["diagram_name"]
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
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"a": 65}
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response["b"] == 8 and \
                   message_response["diagram_execute_status"] == "1"
