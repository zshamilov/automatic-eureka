import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import NodeViewShortInfo, ResponseDto, DiagramViewDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import get_node_by_id, create_node, \
    delete_node_by_id
from products.Decision.utilities.custom_models import IntNodeType
from products.Decision.utilities.node_cunstructors import empty_node_construct


@allure.epic("Диаграммы")
@allure.feature("Узел отправка предложений в Offer Storage")
@pytest.mark.scenario("DEV-9139")
class TestOfferStorageWriteNode:

    @allure.story("Узел отправка предложений в Offer Storage создаётся")
    @allure.title(
        "Создать диаграмму с узлом отправка предложений в Offer Storage без параметров, увидеть, что создался"
    )
    @pytest.mark.offerstorage
    def test_create_node_offer_storage_write(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла отправка предложений в Offer Storage"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.offerStorageWrite,
                                             diagram_version_id=temp_version_id,
                                             node_name="Отправка предложений в Offer Storage")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла корректен и равен отправка предложений в Offer Storage"
        ):
            assert diagram.nodes[str(node_id)].nodeTypeId == IntNodeType.offerStorageWrite

    @allure.story("Узел отправка предложений в Offer Storage удаляется")
    @allure.title(
        "Создать диаграмму с узлом отправка предложений в Offer Storage без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.offerstorage
    def test_delete_node_offer_storage_write(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла отправка предложений в Offer Storage"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.offerStorageWrite,
                                             diagram_version_id=temp_version_id,
                                             node_name="Отправка предложений в Offer Storage")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_id)
        with allure.step("Проверка, что поиск узла вернулся с кодом 404"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_id).status == 404
