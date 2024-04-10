import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import NodeViewShortInfo, DiagramInOutParameterFullViewDto, \
    NodeValidateDto, NodeViewWithVariablesDto, EmbedEnum, ResponseDto, DiagramViewDto, ExternalServiceTechFullViewDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_external_service_api import get_tech_service
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id, create_node, \
    delete_node_by_id
from products.Decision.utilities.commhub_node_constructors import commhub_read_construct
from products.Decision.utilities.custom_models import VariableParams, IntValueType, IntNodeType
from products.Decision.utilities.node_cunstructors import empty_node_construct


@allure.epic("Диаграммы")
@allure.feature("Узел получение истории из CommHub")
@pytest.mark.scenario("DEV-10949")
class TestCommHubReadNode:

    @allure.story("Узел является валидным с незаполненной фильтрацией")
    @allure.title("Создать узел, не заполнять фильтры, провалидировать")
    @pytest.mark.commhub
    @pytest.mark.variable_data(
        [VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_tasks", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Task")])
    @pytest.mark.nodes(["чтение commhub"])
    def test_commhub_without_filters_valid(self, super_user, diagram_constructor):
        with allure.step("Получение информации об объектах"):
            node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение commhub"]
            tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
                **get_tech_service(super_user, node_type="COMMUNICATION_HUB_READ").body[0])
            variable_for_tasks: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_tasks"]
        with allure.step("Заполнение узла чтения из commhub - без фильтраций"):
            node_commhub_up_data = commhub_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                          output_var_name=variable_for_tasks.parameterName,
                                                          output_var_type_id=variable_for_tasks.typeId,
                                                          service_id=tech_service.serviceId,
                                                          service_version_id=tech_service.versionId,
                                                          param_id=variable_for_tasks.parameterId)
            update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_commhub_up_data.nodeTypeId,
                            properties=node_commhub_up_data.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_commhub_read.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert node_view.validFlag

    @allure.story("Узел является валидным со всеми заполненными фильтрами")
    @allure.title("Создать узел, заполнить все фильтры, провалидировать")
    @pytest.mark.commhub
    @pytest.mark.variable_data(
        [VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_tasks", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Task")])
    @pytest.mark.nodes(["чтение commhub"])
    def test_commhub_all_filters_valid(self, super_user, diagram_constructor):
        with allure.step("Получение информации об объектах"):
            node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение commhub"]
            tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
                **get_tech_service(super_user, node_type="COMMUNICATION_HUB_READ").body[0])
            variable_for_tasks: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_tasks"]
        with allure.step("заполнение узла чтения из commhub со всеми фильтрами - дата, каналы, типы разделов"):
            node_commhub_up_data = commhub_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                          output_var_name=variable_for_tasks.parameterName,
                                                          output_var_type_id=variable_for_tasks.typeId,
                                                          service_id=tech_service.serviceId,
                                                          service_version_id=tech_service.versionId,
                                                          channel="SMS",
                                                          embed=[EmbedEnum.BATCHES, EmbedEnum.TEMPLATES],
                                                          created_after="2023-08-01 17:08:44.213",
                                                          created_before="2023-09-01 17:08:44.213",
                                                          param_id=variable_for_tasks.parameterId)
            update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_commhub_up_data.nodeTypeId,
                            properties=node_commhub_up_data.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_commhub_read.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert node_view.validFlag

    @allure.story("Предусмотрены проверки валидации на заполнение полей: Название блока, Указана переменная для "
                  "записи задач, Тип группы, Интервал")
    @allure.title("В узле указать неправильный временной интервал")
    @pytest.mark.commhub
    @pytest.mark.variable_data(
        [VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_tasks", varType="out", isComplex=True, isArray=True, isConst=False,
                        varValue="Task")])
    @pytest.mark.nodes(["чтение commhub"])
    @allure.issue("DEV-19474")
    def test_commhub_time_interval_invalid(self, super_user, diagram_constructor):
        with allure.step("Получение информации об объектах"):
            node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение commhub"]
            tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
                **get_tech_service(super_user, node_type="COMMUNICATION_HUB_READ").body[0])
            variable_for_tasks: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_tasks"]
        with allure.step("заполнение узла чтения из commhub с невалидным временным интервалом(создан до по дате "
                         "раньше, чем после)"):
            node_commhub_up_data = commhub_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                          output_var_name=variable_for_tasks.parameterName,
                                                          output_var_type_id=variable_for_tasks.typeId,
                                                          service_id=tech_service.serviceId,
                                                          service_version_id=tech_service.versionId,
                                                          created_after="2023-09-01 17:08:44.213",
                                                          created_before="2023-08-01 17:08:44.213",
                                                          param_id=variable_for_tasks.parameterId)
            update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_commhub_up_data.nodeTypeId,
                            properties=node_commhub_up_data.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_commhub_read.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert not node_view.validFlag

    @allure.story("Узел получение истории из CommHub создаётся")
    @allure.title(
        "Создать диаграмму с узлом получение истории из CommHub без параметров, увидеть, что создался"
    )
    @pytest.mark.commhub
    def test_create_node_commhub_read(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла коммуникации"):
            node_comms = empty_node_construct(
                x=700, y=202.22915649414062, node_type=IntNodeType.commHubRead,
                diagram_version_id=temp_version_id, node_name="чтение commhub"
            )
            node_comms_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_comms).body
            )
            node_comms_id = node_comms_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла корректен и равен коммуникации"
        ):
            assert diagram.nodes[str(node_comms_id)].nodeTypeId == IntNodeType.commHubRead

    @allure.story("Узел коммуникации удаляется")
    @allure.title(
        "Создать диаграмму с узлом коммуникации без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.commhub
    def test_delete_node_commhub_read(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла коммуникации"):
            node_comms = empty_node_construct(
                x=700, y=202.22915649414062, node_type=IntNodeType.commHubRead,
                diagram_version_id=temp_version_id, node_name="чтение commhub"
            )
            node_comms_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_comms).body
            )
            node_comms_id = node_comms_response.uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_comms_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_comms_id).status == 404
