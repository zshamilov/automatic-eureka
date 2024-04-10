import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, deploy_config
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.custom_code_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Кастомный код")
@allure.feature("Кастомный код")
class TestRuntimeCustomCode:
    @allure.story(
        "Диаграмма с узлом кастомный код-python отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом кастомный код-python на развёртование, проверить, что появилась в списке деплоев"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    def test_submit_diagram_script_node_python(self, super_user, diagram_custom_code_python_2):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_custom_code_python_2["diagram_id"]
            diagram_name = diagram_custom_code_python_2["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлом кастомный код-python и окружением  отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом кастомный код-python на развёртование, проверить, что появилась в списке деплоев"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    def test_submit_diagram_script_node_python_environment(self, super_user, diagram_custom_code_python_environment):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_custom_code_python_environment["diagram_id"]
            diagram_name = diagram_custom_code_python_environment["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "В диаграмму с узлом кастомный код-python возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом кастомный код-python, получить ответ"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    def test_send_message_diagram_with_script_node_python(self, super_user,
                                                          diagram_python_script_submit_2,
                                                          deploy_diagrams_gen,
                                                          integration_user):
        env_id = diagram_python_script_submit_2["env_id"]
        deploy_id = diagram_python_script_submit_2["deploy_id"]
        diagram_id = diagram_python_script_submit_2["diagram_id"]
        diagram_name = diagram_python_script_submit_2["diagram_name"]
        diagram_param = diagram_python_script_submit_2["diagram_param"]
        with allure.step("Деплой подготовленной диаграммы"):
            deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получить настройки развёрнутого деплоя"):
            actual_config: DeployConfigurationFullDto = DeployConfigurationFullDto(
                **deploy_config(super_user, deploy_version_id=deploy_id)
            )
            call_uri = actual_config.callUri
        with allure.step("Отправка сообщения в развёрнутый диеплой"):
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{diagram_param.parameterName}": 1},
            ).body
        with allure.step("Пришло значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param.parameterName}"] is not None and \
                   message_response["diagram_execute_status"] == "1"

    @allure.story(
        "Диаграмма с узлом кастомный код-groovy отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом кастомный код-groovy на развёртование, проверить, что появилась в списке деплоев"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    def test_submit_diagram_script_node_groovy(self, super_user, diagram_custom_code_groovy_2):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_custom_code_groovy_2["diagram_id"]
            diagram_name = diagram_custom_code_groovy_2["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "В диаграмму с узлом кастомный код-groovy возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом кастомный код-groovy, получить ответ"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    def test_send_message_diagram_with_script_node_groovy(self, super_user,
                                                          diagram_groovy_script_submit_2,
                                                          deploy_diagrams_gen,
                                                          integration_user):
        env_id = diagram_groovy_script_submit_2["env_id"]
        deploy_id = diagram_groovy_script_submit_2["deploy_id"]
        diagram_id = diagram_groovy_script_submit_2["diagram_id"]
        diagram_name = diagram_groovy_script_submit_2["diagram_name"]
        diagram_param = diagram_groovy_script_submit_2["diagram_param"]
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
                body={f"{diagram_param.parameterName}": 1},
            ).body
        with allure.step("Пришло значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param.parameterName}"] is not None and \
                   message_response["diagram_execute_status"] == "1"
