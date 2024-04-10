import uuid
import time

import allure
import pytest

from products.Decision.framework.model import DeployConfigurationFullDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.offer_storage_read_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType
from products.Decision.runtime_tests.runtime_fixtures.offer_storage_write_fixtures import offer_storage_write_with_offer


@allure.epic("Узел выгрузка предложений из Offer Storage")
@allure.feature("Узел выгрузка предложений из Offer Storage")
@pytest.mark.scenario("DEV-18683")
class TestRuntimeOfferStorageRead:

    @allure.story("Диаграмма с узлом выгрузки предложений из Offer Storage с чтением по клиенту отправляется на "
                  "развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом выгрузки предложений из Offer Storage с чтением по клиенту, проверить, "
        "что готова к развертыванию")
    @pytest.mark.offerstorage
    @pytest.mark.variable_data(
        [VariableParams(varName="in_offer_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="read_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")])
    @pytest.mark.nodes(["чтение OS"])
    @pytest.mark.parametrize("offer_storage_read_client_service", [1, None], indirect=True)
    def test_submit_offer_storage_read_client(self, super_user, offer_storage_read_client_service):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_read_client_service["diagram_data"].diagramId
            diagram_name = offer_storage_read_client_service["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story("Диаграмма с узлом выгрузки предложений из Offer Storage с чтением по id предложения отправляется на "
                  "развертывание")
    @allure.title(
        "Развернуть диаграмму с узлом выгрузки предложений из Offer Storage с чтением по id предложения, проверить, "
        "что готова к развертыванию")
    @pytest.mark.offerstorage
    @pytest.mark.variable_data(
        [VariableParams(varName="in_offer_id", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="read_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")])
    @pytest.mark.nodes(["чтение OS"])
    def test_submit_offer_storage_read_offer(self, super_user, offer_storage_read_offer_service):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_read_offer_service["diagram_data"].diagramId
            diagram_name = offer_storage_read_offer_service["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлами: Предложение -> Отправка предложений в OS -> Выгрузка предложений из OS возвращает "
        "корректное количество предложений, соответствующих фильтрам")
    @pytest.mark.offerstorage
    @allure.title("Отправить сообщение в диаграмму с узлами Предложение -> Отправка предложений в OS -> Выгрузка "
                  "предложений из OS, проверить, что вернулось правильное количество предложений")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_offer_product_code", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_offer_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_client_id_type", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_control_group", varType="in", varDataType=IntValueType.bool.value),
         VariableParams(varName="in_offer_score", varType="in", varDataType=IntValueType.float.value),
         VariableParams(varName="in_offer_start_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="in_offer_end_at", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer"),
         VariableParams(varName="read_offers", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Offer")
         ])
    @pytest.mark.nodes(["предложение", "запись OS", "чтение OS"])
    @pytest.mark.parametrize("offer_storage_read_client_service", [1, None], indirect=True)
    def test_send_message_offer_storage_read(self, super_user, integration_user,
                                             offer_storage_write_with_offer,
                                             offer_storage_read_client_service, get_env,
                                             deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = offer_storage_read_client_service["diagram_data"].diagramId
            diagram_name = offer_storage_read_client_service["diagram_name"]
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
            client_id = generate_string(6)
            client_id_type = offer_storage_read_client_service["client_type"]
            control_group = True
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
            product_code = str(uuid.uuid4())
            offer_id = str(uuid.uuid4())
            message_response2 = send_message(
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
            assert len(message_response["read_offers"]) == 1 and \
                   len(message_response2["read_offers"]) == offer_storage_read_client_service["offer_count_check"] and \
                   message_response["diagram_execute_status"] == "1"
