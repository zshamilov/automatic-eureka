import time

import allure
import pytest

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, deploy_config
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message


@allure.epic("Вызов Внешнего Сервиса")
@allure.feature("Вызов Внешнего Сервиса")
class TestRuntimeExtService:
    @allure.story(
        "Диаграмма с узлом вызова внешнего сервиса отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом вызова внешнего сервиса на развёртование, проверить, что появилась в списке "
        "деплоев "
    )
    def test_submit_diagram_ext_serv_node(self, super_user, diagram_external_service_saved):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_external_service_saved["template"].diagramId
            diagram_name = diagram_external_service_saved["diagram_name"]
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
        "В диаграмму с узлом вызова внешнего сервиса возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом вызова внешнего сервиса, получить ответ"
    )
    @pytest.mark.environment_dependent
    def test_send_message_diagram_with_ext_serv_node(self, super_user,
                                                     diagram_ext_serv_submit,
                                                     deploy_diagrams_gen,
                                                     integration_user):
        env_id = diagram_ext_serv_submit["env_id"]
        deploy_id = diagram_ext_serv_submit["deploy_id"]
        diagram_id = diagram_ext_serv_submit["diagram_id"]
        diagram_name = diagram_ext_serv_submit["diagram_name"]
        in_diagram_param = diagram_ext_serv_submit["in_diagram_param"]
        out_diagram_param = diagram_ext_serv_submit["out_diagram_param"]
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
                body={f"{in_diagram_param.parameterName}": "give_me_cat_weight"},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{out_diagram_param.parameterName}"] == 3.2 and \
                    message_response["diagram_execute_status"] == "1"

