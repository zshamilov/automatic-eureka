import time
from datetime import datetime, timedelta

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.policy_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType, SystemCTypes


@allure.epic("Узел RTF-Policy. Проверка контактной политики")
@allure.feature("Узел RTF-Policy. Проверка контактной политики")
@pytest.mark.scenario("DEV-10955")
class TestRuntimePolicy:

    @allure.story(
        "Диаграмма с узлом 'RTF-Policy. Проверка контактной политики' без флагов отправляется на развертывание")
    @allure.title(
        "Отправить на развертывание диаграмму с узлом 'RTF-Policy. Проверка контактной политики' без флагов, проверить,"
        "что готова к развертыванию")
    @pytest.mark.policy
    @pytest.mark.variable_data(
        [VariableParams(varName="in_client_id_var", varType="in", varDataType=IntValueType.str),
         VariableParams(varName="in_contact_dt_var", varType="in", varDataType=IntValueType.str),
         VariableParams(varName="out_policy", varType="out", varDataType=SystemCTypes.check_policy_result.value,
                        isComplex=True, isConst=False,
                        varValue="out_policy")])
    @pytest.mark.nodes(["проверка policy"])
    def test_submit_policy_no_flags(self, super_user, policy_without_flags):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = policy_without_flags["diagram_data"].diagramId
            diagram_name = policy_without_flags["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлом 'RTF-Policy. Проверка контактной политики' без флагов возвращает корректный ответ с "
        "результатом проверки")
    @allure.title("Отправить сообщение в диаграмму с узлом 'RTF-Policy. Проверка контактной политики' без флагов,"
                  "проверить, что вернулся результат проверки")
    @pytest.mark.policy
    @pytest.mark.variable_data(
        [VariableParams(varName="in_client_id_var", varType="in", varDataType=IntValueType.str),
         VariableParams(varName="in_contact_dt_var", varType="in", varDataType=IntValueType.str),
         VariableParams(varName="out_policy", varType="out", varDataType=SystemCTypes.check_policy_result.value,
                        isComplex=True, isConst=False,
                        varValue="out_policy")])
    @pytest.mark.nodes(["проверка policy"])
    def test_send_message_policy_no_flags(self, super_user, integration_user,
                                          policy_without_flags, get_env,
                                          deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = policy_without_flags["diagram_data"].diagramId
            diagram_name = policy_without_flags["diagram_name"]
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
            client_id = "decision_autotest_"+generate_string()
            tomorrow = datetime.now() + timedelta(days=1)
            in_contact_dt_var_val = tomorrow.isoformat()[:-3] + "Z"

            time.sleep(5)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={'in_client_id_var': client_id,
                      'in_contact_dt_var': in_contact_dt_var_val},
            ).body
        with allure.step(
                "Проверка, что в ответе диаграммы сохранился идентификатор клиента, диаграмма успешно отработало"
                "и есть результат по проверке клиента"):
            assert message_response["out_policy"]["clientId"] == client_id \
                   and message_response["diagram_execute_status"] == "1" \
                   and message_response["out_policy"]["complianceCheckResult"] in ["REJECTED", "ALLOWED",
                                                                                   "UNSUBSCRIBED", "ERROR"]

    @allure.story(
        "Диаграмма с узлом 'RTF-Policy. Проверка контактной политики' со всеми флагами отправляется на развертывание")
    @allure.title(
        "Отправить на развертывание диаграмму с узлом 'RTF-Policy. Проверка контактной политики' со всеми флагами, "
        "проверить, что готова к развертыванию")
    @pytest.mark.policy
    @pytest.mark.variable_data(
        [VariableParams(varName="in_client_id_var", varType="in", varDataType=IntValueType.str),
         VariableParams(varName="out_policy", varType="out", varDataType=SystemCTypes.check_policy_result.value,
                        isComplex=True, isConst=False,
                        varValue="out_policy")])
    @pytest.mark.nodes(["проверка policy"])
    def test_submit_policy_all_flags(self, super_user, policy_with_all_flags):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = policy_with_all_flags["diagram_data"].diagramId
            diagram_name = policy_with_all_flags["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлом 'RTF-Policy. Проверка контактной политики' со всеми флагами возвращает ответ с "
        "результатом проверки")
    @allure.title("Отправить сообщение в диаграмму с узлом 'RTF-Policy. Проверка контактной политики' со всеми флагами,"
                  "проверить, что вернулся результат проверки")
    @pytest.mark.policy
    @pytest.mark.variable_data(
        [VariableParams(varName="in_client_id_var", varType="in", varDataType=IntValueType.str),
         VariableParams(varName="out_policy", varType="out", varDataType=SystemCTypes.check_policy_result.value,
                        isComplex=True, isConst=False,
                        varValue="out_policy")])
    @pytest.mark.nodes(["проверка policy"])
    def test_send_message_policy_all_flags(self, super_user, integration_user,
                                           policy_with_all_flags, get_env,
                                           deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = policy_with_all_flags["diagram_data"].diagramId
            diagram_name = policy_with_all_flags["diagram_name"]
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
        with allure.step("Отправка сообщений в развёрнутую диаграмму"):
            client_id = "decision_autotest_"+generate_string()

            time.sleep(5)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={'in_client_id_var': client_id},
            ).body
        with allure.step(
                "Проверка, что в ответе диаграммы сохранился идентификатор клиента, диаграмма успешно отработало"
                "и есть результат по проверке клиента"):
            assert message_response["out_policy"]["clientId"] == client_id \
                   and message_response["diagram_execute_status"] == "1" \
                   and message_response["out_policy"]["complianceCheckResult"] in ["REJECTED", "ALLOWED",
                                                                                   "UNSUBSCRIBED", "ERROR"]
