import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, ExternalServiceTechFullViewDto, DiagramInOutParameterFullViewDto, \
    NodeViewWithVariablesDto, NodeUpdateDto, DiagramViewDto, OfferStorageClientIdTypesFullDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_external_service_api import get_tech_service
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.framework.steps.decision_steps_offer_storage_api import get_offer_storage_client_id_types
from products.Decision.utilities.offer_storage_node_constructors import os_read_client_construct, \
    os_read_offer_construct


@pytest.fixture()
def offer_storage_read_client_service(super_user, diagram_constructor, save_diagrams_gen, request):
    """
    Параметризованная фикстура для создания диаграммы с настроенным узлом Выгрузка предложений из Offer Storage с
    выгрузкой по id клиента указанного в pytest.mark.parametrize количества offer-ов, соответствующих значениям
    фильтров - True
    """
    offer_count = request.param
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_os_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение OS"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="OFFER_STORAGE_READ_BY_CLIENT_ID").body[0])
    variable_for_offers: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["read_offers"]
    os_client_id_type_resp: OfferStorageClientIdTypesFullDto = OfferStorageClientIdTypesFullDto.construct(
        **get_offer_storage_client_id_types(super_user).body
    )
    client_type = os_client_id_type_resp.clientIdTypes[0]["description"]
    input_var_client_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_client_id"]
    node_offer_storage_up_data = os_read_client_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                          service_id=tech_service.serviceId,
                                                          service_version_id=tech_service.versionId,
                                                          client_id_type=client_type,
                                                          client_var_name=input_var_client_id.parameterName,
                                                          client_var_type_id=input_var_client_id.typeId,
                                                          client_v_param_id=input_var_client_id.parameterId,
                                                          output_var_name=variable_for_offers.parameterName,
                                                          output_var_type_id=variable_for_offers.typeId,
                                                          param_id=variable_for_offers.parameterId,
                                                          active_channel_flag=True,
                                                          active_flag=True,
                                                          control_flag=True,
                                                          default_offers_flag=True,
                                                          offer_count=offer_count)
    update_node(super_user, node_id=node_os_read.nodeId, body=node_offer_storage_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_os_read_client" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    if offer_count is None:
        offer_count_check = 2
    else:
        offer_count_check = 1
    return {"diagram_name": new_diagram_name, "diagram_data": save_data, "client_type": client_type,
            "offer_count_check": offer_count_check}


@pytest.fixture()
def offer_storage_read_offer_service(super_user, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом Выгрузка предложений из Offer Storage с выгрузкой по id предложения
    offer-а, соответствующего значению фильтра - True
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_os_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение OS"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="OFFER_STORAGE_READ_BY_OFFER_ID").body[0])
    variable_for_offers: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["read_offers"]
    input_var_offer_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_id"]
    node_offer_storage_up_data = os_read_offer_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                         service_id=tech_service.serviceId,
                                                         service_version_id=tech_service.versionId,
                                                         output_var_name=variable_for_offers.parameterName,
                                                         output_var_type_id=variable_for_offers.typeId,
                                                         param_id=variable_for_offers.parameterId,
                                                         ext_offer_id_var_name=input_var_offer_id.parameterName,
                                                         ext_offer_id_var_type=input_var_offer_id.typeId,
                                                         ext_offer_id_v_param_id=input_var_offer_id.parameterId,
                                                         active_channel_flag=True)
    update_node(super_user, node_id=node_os_read.nodeId, body=node_offer_storage_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_os_read_offer" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    return {"diagram_name": new_diagram_name, "diagram_data": save_data}
