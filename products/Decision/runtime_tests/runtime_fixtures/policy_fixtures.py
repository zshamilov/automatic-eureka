import uuid
from typing import List

import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, ExternalServiceTechFullViewDto, \
    DiagramInOutParameterFullViewDto, \
    NodeViewWithVariablesDto, NodeUpdateDto, DiagramViewDto, AdditionalParameters, SimpleVariableProperties
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_external_service_api import get_tech_service
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.framework.steps.decision_steps_policy_api import get_policy_attributes
from products.Decision.utilities.policy_node_constructors import policy_node_construct


@pytest.fixture()
def policy_without_flags(super_user, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом 'RTF-Policy. Проверка контактной политики' без флагов в узле
    и дополнительных параметров ответа
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_policy: NodeViewShortInfo = diagram_constructor["nodes"]["проверка policy"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]

    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="POLICY_READ").body[0])
    in_client_id_var = diagram_constructor["variables"]["in_client_id_var"]
    in_contact_dt_var = diagram_constructor["variables"]["in_contact_dt_var"]
    contact_dt = '$' + diagram_constructor["variables"]["in_contact_dt_var"].parameterName
    variable_for_policy: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_policy"]

    node_policy_up_data = policy_node_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                node_output_var=variable_for_policy,
                                                client_id_var=in_client_id_var,
                                                ext_service=tech_service,
                                                contact_date_time=contact_dt)
    update_node(super_user, node_id=node_policy.nodeId, body=node_policy_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "kk_test_diagram_policy" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data, "in_client_id_var": in_client_id_var,
            "in_contact_dt_var": in_contact_dt_var}


@pytest.fixture()
def policy_with_all_flags(super_user, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом 'RTF-Policy. Проверка контактной политики' со всеми флагами в узле
    и дополнительными параметров ответа
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_policy: NodeViewShortInfo = diagram_constructor["nodes"]["проверка policy"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]

    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="POLICY_READ").body[0])

    in_client_id_var = diagram_constructor["variables"]["in_client_id_var"]

    variable_for_policy: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_policy"]

    # из-за бага DEV-22113 в документации пока нет подходящего дто и без расспаковки
    # policy_attributes: List[ChannelFullViewDto] = [
    #     ChannelFullViewDto.construct(**attr) for attr in get_policy_attributes(super_user).body]

    policy_attributes = get_policy_attributes(super_user).body
    additional_policy_resp_params: List[AdditionalParameters] = \
        [AdditionalParameters.construct(key=attr['key'],
                                        value=SimpleVariableProperties.construct(variableName=attr["values"][0]['key']),
                                        rowKey=str(uuid.uuid4()),
                                        isValueFromDict=True) for attr in policy_attributes]

    node_policy_up_data = policy_node_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                node_output_var=variable_for_policy,
                                                client_id_var=in_client_id_var,
                                                ext_service=tech_service,
                                                dry_run=True,
                                                weak=True,
                                                additional_parameters=additional_policy_resp_params)
    update_node(super_user, node_id=node_policy.nodeId, body=node_policy_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "kk_test_diagram_policy" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data,
            "in_client_id_var": in_client_id_var}
