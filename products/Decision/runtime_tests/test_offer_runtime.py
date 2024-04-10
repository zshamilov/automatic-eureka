import time

import allure

from products.Decision.framework.model import DiagramInOutParameterFullViewDto, DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, deploy_config
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message


@allure.epic("Предложение")
@allure.feature("Предложение")
class TestRuntimeOffer:
    @allure.story("Диаграмма с узлом предложения отправляется на развёртывание")
    @allure.title("Создать диаграмму, отправить на развертывание, проверить, что успешно")
    def test_submit_diagram_offer(self, super_user, diagram_offer_for_runtime):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_offer_for_runtime["diagram_id"]
            diagram_name = diagram_offer_for_runtime["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
            # submit_response = put_diagram_submit(super_user, version_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("В диаграмму с узлом предложения можно отправить сообщение в простом сценарии")
    @allure.title("Развернуть диаграмму с узлом предложения, проверить, что сообщение соответствует ожиданиям")
    def test_send_message_diagram_offer(self, super_user,
                                        integration_user,
                                        diagram_offer_submit,
                                        deploy_diagrams_gen):
        env_id = diagram_offer_submit["env_id"]
        deploy_id = diagram_offer_submit["deploy_id"]
        diagram_id = diagram_offer_submit["diagram_id"]
        diagram_name = diagram_offer_submit["diagram_name"]
        diagram_param_in: DiagramInOutParameterFullViewDto = diagram_offer_submit["diagram_param_in"]
        diagram_param_out: DiagramInOutParameterFullViewDto = diagram_offer_submit["diagram_param_out"]
        in_message_value = 5
        with allure.step("Деплой подготовленной диаграммы"):
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получить настройки развёрнутого деплоя"):
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{diagram_param_in.parameterName}": in_message_value},
            ).body
        with allure.step("Пришло значение выходной переменной"):
            assert message_response[f"{diagram_param_out.parameterName}"] is not None
        with allure.step("Пришло значение атрибута выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param_out.parameterName}"][0]["offerId"] is not None and \
                   message_response["diagram_execute_status"] == "1"
