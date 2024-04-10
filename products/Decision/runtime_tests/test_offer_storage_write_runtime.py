import time
import uuid

import allure
import pytest

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.offer_storage_write_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Узел отправка предложений в Offer Storage")
@allure.feature("Узел отправка предложений в Offer Storage")
@pytest.mark.scenario("DEV-9139")
class TestRuntimeOfferStorageWrite:

    @allure.story("Диаграмма с узлом отправка предложений в Offer Storage без флага отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом отправка предложений в Offer Storage без флага, проверить, что готова к "
        "развертыванию")
    @pytest.mark.offerstorage
    @pytest.mark.variable_data(
        [VariableParams(varName="out_offers", varType="in_out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")])
    @pytest.mark.nodes(["запись OS"])
    def test_submit_offer_storage_write(self, super_user, offer_storage_write_without_flag):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_write_without_flag["diagram_data"].diagramId
            diagram_name = offer_storage_write_without_flag["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлами предложение, отправка предложений в Offer Storage без флага продолжения работы и расчет "
        "переменных отправляется на развертывание")
    @allure.title(
        "Развернуть диаграмму с узлами предложение, отправка предложений в Offer Storage без флага продолжения работы "
        "и расчет переменных, проверить, что готова к развертыванию")
    @pytest.mark.offerstorage
    @pytest.mark.variable_data(
        [VariableParams(varName="in_offer_product_code", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_offer_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id_type", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_control_group", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_offer_score", varType="in", varDataType=IntValueType.float.value),
         VariableParams(varName="in_offer_start_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_end_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_int"),
         VariableParams(varName="out_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")])
    @pytest.mark.nodes(["предложение", "запись OS", "расчет переменной"])
    def test_submit_offer_storage_write_without_flag(self, super_user, offer_storage_write_with_offer_and_calc):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_write_with_offer_and_calc["diagram_data"].diagramId
            diagram_name = offer_storage_write_with_offer_and_calc["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлом отправка предложений в Offer Storage без флага продолжения работы НЕ продолжает работу при "
        "частичной записи предложений")
    @allure.title("Отправить сообщение в диаграмму с узлами предложение, отправка предложений в Offer Storage без "
                  "флага продолжения работы без флага продолжения работы при частичной записи и расчет переменных, "
                  "проверить, что ответ корректный")
    @pytest.mark.offerstorage
    @pytest.mark.variable_data(
        [VariableParams(varName="in_offer_product_code", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_offer_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id_type", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_control_group", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_offer_score", varType="in", varDataType=IntValueType.float.value),
         VariableParams(varName="in_offer_start_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_end_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_int"),
         VariableParams(varName="out_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")])
    @pytest.mark.nodes(["предложение", "запись OS", "расчет переменной"])
    def test_send_message_offer_storage_write_without_flag(self, super_user, integration_user,
                                                           offer_storage_write_with_offer_and_calc, get_env,
                                                           deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_write_with_offer_and_calc["diagram_data"].diagramId
            diagram_name = offer_storage_write_with_offer_and_calc["diagram_name"]
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
            product_code = "product_code"
            offer_id = str(uuid.uuid4())
            client_id = "25"
            client_id_type = "customer"
            control_group = False
            score = 1.1
            start_at = "2023-07-10T14:10:20.111+01:00"
            end_at = "2024-08-10T14:10:20.111+01:00"
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_offer_product_code": product_code,
                      "in_offer_offer_id": offer_id,
                      "in_offer_client_id": client_id,
                      "in_offer_client_id_type": client_id_type,
                      "in_offer_control_group": control_group,
                      "in_offer_score": score,
                      "in_offer_start_at": start_at,
                      "in_offer_end_at": end_at},
            ).body
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_offer_product_code": product_code,
                      "in_offer_offer_id": offer_id,
                      "in_offer_client_id": client_id,
                      "in_offer_client_id_type": client_id_type,
                      "in_offer_control_group": control_group,
                      "in_offer_score": score,
                      "in_offer_start_at": start_at,
                      "in_offer_end_at": end_at},
            ).body
        with allure.step("Проверка, что расчет переменной после узла отправка предложений в Offer Storage не "
                         "произошел, статус отработки диаграммы 0 - с ошибкой и текст ошибки корректный"):
            assert message_response["out_int"] is None and message_response["diagram_execute_status"] == "0" and \
                   message_response["errorTrace"] == "Не все предложения были успешно записаны в Offer Storage"

    @allure.story(
        "Диаграмма с узлом отправка предложений в Offer Storage с флагом продолжения работы продолжает работу при "
        "частичной записи предложений")
    @allure.title("Отправить сообщение в диаграмму с узлами предложение и отправка предложений в Offer Storage "
                  "с флагом продолжения работы при частичной записи, проверить, что ответ корректный")
    @pytest.mark.offerstorage
    @pytest.mark.variable_data(
        [VariableParams(varName="in_offer_product_code", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_offer_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id_type", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_control_group", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_offer_score", varType="in", varDataType=IntValueType.float.value),
         VariableParams(varName="in_offer_start_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_end_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_int"),
         VariableParams(varName="out_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")])
    @pytest.mark.nodes(["предложение", "запись OS", "расчет переменной"])
    @pytest.mark.continue_flg(True)
    def test_send_message_offer_storage_write_with_flag(self, super_user, integration_user,
                                                        offer_storage_write_with_offer_and_calc, get_env,
                                                        deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_write_with_offer_and_calc["diagram_data"].diagramId
            diagram_name = offer_storage_write_with_offer_and_calc["diagram_name"]
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
            product_code = "product_code"
            offer_id = str(uuid.uuid4())
            client_id = "25"
            client_id_type = "customer"
            control_group = False
            score = 1.1
            start_at = "2023-07-10T14:10:20.111+01:00"
            end_at = "2024-08-10T14:10:20.111+01:00"
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_offer_product_code": product_code,
                      "in_offer_offer_id": offer_id,
                      "in_offer_client_id": client_id,
                      "in_offer_client_id_type": client_id_type,
                      "in_offer_control_group": control_group,
                      "in_offer_score": score,
                      "in_offer_start_at": start_at,
                      "in_offer_end_at": end_at},
            ).body
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_offer_product_code": product_code,
                      "in_offer_offer_id": offer_id,
                      "in_offer_client_id": client_id,
                      "in_offer_client_id_type": client_id_type,
                      "in_offer_control_group": control_group,
                      "in_offer_score": score,
                      "in_offer_start_at": start_at,
                      "in_offer_end_at": end_at},
            ).body
        with allure.step("Проверка, что произошел расчет переменной после узла отправка предложений в Offer Storage, "
                         "статус отработки диаграммы 0 - с ошибкой и текст ошибки корректный"):
            assert message_response["out_int"] == 5 and message_response["diagram_execute_status"] == "1" and \
                   message_response["out_offers"][0]["detail"] == "Предложение уже существует"

    @allure.story(
        "В диаграмму с узлом отправки предложений в OS можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлами предложение и отправка предложений в Offer Storage "
                  "без флага продолжения работы при частичной записи, проверить, что ответ корректный")
    @pytest.mark.offerstorage
    @pytest.mark.variable_data(
        [VariableParams(varName="in_offer_product_code", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_offer_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id_type", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_control_group", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_offer_score", varType="in", varDataType=IntValueType.float.value),
         VariableParams(varName="in_offer_start_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_end_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_int"),
         VariableParams(varName="out_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")])
    @pytest.mark.nodes(["предложение", "запись OS", "расчет переменной"])
    def test_send_message_offer_storage(self, super_user, integration_user,
                                        offer_storage_write_with_offer_and_calc, get_env, deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_write_with_offer_and_calc["diagram_data"].diagramId
            diagram_name = offer_storage_write_with_offer_and_calc["diagram_name"]
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
            product_code = str(uuid.uuid4())
            offer_id = str(uuid.uuid4())
            client_id = "25"
            client_id_type = "customer"
            control_group = False
            score = 1.1
            start_at = "2023-07-10T14:10:20.111+01:00"
            end_at = "2024-08-10T14:10:20.111+01:00"
            time.sleep(10)
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={"in_offer_product_code": product_code,
                      "in_offer_offer_id": offer_id,
                      "in_offer_client_id": client_id,
                      "in_offer_client_id_type": client_id_type,
                      "in_offer_control_group": control_group,
                      "in_offer_score": score,
                      "in_offer_start_at": start_at,
                      "in_offer_end_at": end_at},
            ).body
        with allure.step("Проверка, что пришло правильное значение выходной переменной и статус исполнения диаграммы "
                         "1 - без ошибок"):
            assert message_response["out_int"] == 5 and message_response["out_offers"] is not None and message_response[
                "diagram_execute_status"] == "1"
