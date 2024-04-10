import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, DiagramViewDto, NodeViewShortInfo
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import create_node, delete_node_by_id, get_node_by_id
from products.Decision.utilities.custom_models import IntNodeType
from products.Decision.utilities.node_cunstructors import empty_node_construct


@allure.epic("Диаграммы")
@allure.feature("Узел отправка задач в Communicaton Hub")
@pytest.mark.scenario("DEV-8480")
class TestDiagramsComHubSendNode:
    @allure.story("Узел отправка задач в Communicaton Hub создаётся")
    @allure.title(
        "Создать диаграмму с узлом отправка задач в Communicaton Hub без параметров, увидеть, что создался"
    )
    @pytest.mark.commhub
    def test_create_node_comm_hub_write(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла отправка задач в Communicaton Hub"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.communicationHub,
                                             diagram_version_id=temp_version_id,
                                             node_name="Отправка задач в Communicaton Hub")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла корректен и равен отправка задач в Communicaton Hub"
        ):
            assert diagram.nodes[str(node_id)].nodeTypeId == IntNodeType.communicationHub

    @allure.story("Узел отправка задач в Communicaton Hub удаляется")
    @allure.title(
        "Создать диаграмму с узлом отправка задач в Communicaton Hub без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.commhub
    def test_delete_node_comm_hub_write(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла отправка задач в Communicaton Hub"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.communicationHub,
                                             diagram_version_id=temp_version_id,
                                             node_name="Отправка задач в Communicaton Hub")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_id)
        with allure.step("Проверка, что поиск узла вернулся с кодом 404"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_id).status == 404
