import time

import allure

from products.Decision.framework.model import DiagramInOutParameterFullViewDto, DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, \
    find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message


@allure.epic("Начало/Завершение")
@allure.feature("Начало/Завершение")
class TestRuntimeStartFinish:
    @allure.story("Диаграмма с узлами начало, завершение отправляется на развёртку")
    @allure.title("Создать диаграмму, отправить на развертывание, проверить, что успешно")
    def test_submit_diagram_start_finish(self, super_user, simple_diagram):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = simple_diagram
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
            diagram_name = create_and_save_result["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
            # submit_response = put_diagram_submit(super_user, version_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("В диаграмму с узлами начало, завершение возможно отправить сообщение")
    @allure.title("Отправить в диаграмму с узлами начало, завершение сообщение, получить ответ")
    # @pytest.mark.skip(reason="swagger coverage fix")
    def test_send_message_diagram_start_finish(
            self,
            super_user,
            integration_user,
            get_env,
            simple_diagram,
            deploy_diagrams_gen,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
            diagram_param: DiagramInOutParameterFullViewDto = create_and_save_result[
                "diagram_param"
            ]
            diagram_name = create_and_save_result["diagram_name"]
        with allure.step("Отправка диаграммы на сабмит"):
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
                body={f"{diagram_param.parameterName}": 21},
            ).body
        with allure.step("Пришло правильное значение выходной переменной и статус исполнения диаграммы 1 - без ошибок"):
            assert message_response[f"{diagram_param.parameterName}"] == 21 and \
                   message_response["diagram_execute_status"] == "1"
