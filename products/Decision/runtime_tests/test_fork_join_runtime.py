import time

import allure

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, deploy_config
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message


@allure.epic("Fork/Join")
@allure.feature("Fork/Join")
class TestRuntimeForkJoin:
    @allure.story(
        "Диаграмма с узлами fork-join отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлами fork-join на развёртование, проверить, что появилась в списке деплоев"
    )
    def test_submit_diagram_fork_join_node(self, super_user, diagram_fork_join_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_fork_join_saved["template"].diagramId
            diagram_name = diagram_fork_join_saved["diagram_name"]
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
        "В диаграмму с узлами fork-join возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлами fork-join, получить ответ"
    )
    def test_send_message_diagram_with_fork_join_node(self, super_user,
                                                      diagram_fork_join_submit,
                                                      deploy_diagrams_gen,
                                                      integration_user):
        env_id = diagram_fork_join_submit["env_id"]
        deploy_id = diagram_fork_join_submit["deploy_id"]
        diagram_id = diagram_fork_join_submit["diagram_id"]
        diagram_name = diagram_fork_join_submit["diagram_name"]
        diagram_param = diagram_fork_join_submit["diagram_param"]
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
                body={f"{diagram_param.parameterName}": 10},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param.parameterName}"] == 1 and \
                   message_response["diagram_execute_status"] == "1"
