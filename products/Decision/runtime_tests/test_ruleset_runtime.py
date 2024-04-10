import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.ruleset_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Набор правил")
@allure.feature("Набор правил")
class TestRuntimeRuleset:
    @allure.story(
        "Диаграмма с узлом набор правил отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом набор правил на развёртование, проверить, что появилась в списке деплоев"
    )
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_rule_result", varType="out", varDataType=IntValueType.complex_type_rule.value,
                        isComplex=True, isArray=True, isConst=False)])
    @pytest.mark.nodes(["набор правил"])
    def test_submit_diagram_ruleset_node(self, super_user, diagram_ruleset_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_ruleset_saved["diagram_data"].diagramId
            diagram_name = diagram_ruleset_saved["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "В диаграмму с узлом набор правил возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом набор правил, получить ответ"
    )
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_rule_result", varType="out", varDataType=IntValueType.complex_type_rule.value,
                        isComplex=True, isArray=True, isConst=False)])
    @pytest.mark.nodes(["набор правил"])
    def test_send_message_diagram_with_ruleset_node(self, super_user,
                                                    diagram_ruleset_saved,
                                                    get_env,
                                                    deploy_diagrams_gen,
                                                    integration_user):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_ruleset_saved["diagram_data"].diagramId
            diagram_name = diagram_ruleset_saved["diagram_name"]
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
                body={"input_var": 10},
            ).body
            message_response2 = send_message(
                integration_user,
                call_uri=call_uri,
                body={"input_var": 4},
            ).body
        with allure.step("Пришло значение выходной переменной в обоих сообщениях"):
            assert message_response1["out_rule_result"] is not None
            assert message_response2["out_rule_result"] is not None
        with allure.step("Пришли правильные значения атрибутов выходных переменных и статус исполнения диаграммы 1 - "
                         "без ошибок"):
            if message_response1["out_rule_result"][0]["RuleResult"] == True and \
                    message_response1["diagram_execute_status"] == "1":
                first_cond_correct = True
            if message_response2["out_rule_result"][0]["RuleResult"] == True and \
                    message_response2["diagram_execute_status"] == "1":
                second_cond_correct = True
            assert first_cond_correct
            assert second_cond_correct
