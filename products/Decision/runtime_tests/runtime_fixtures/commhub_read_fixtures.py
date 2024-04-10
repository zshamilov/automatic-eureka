import datetime

import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, ExternalServiceTechFullViewDto, \
    DiagramInOutParameterFullViewDto, NodeViewWithVariablesDto, NodeUpdateDto, DiagramViewDto, VariablePropertiesBase, \
    EmbedEnum
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_external_service_api import get_tech_service
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.utilities.commhub_node_constructors import commhub_read_construct


@pytest.fixture()
def commhub_read_without_filters(super_user, diagram_constructor, save_diagrams_gen):
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение commhub"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="COMMUNICATION_HUB_READ").body[0])
    variable_for_tasks: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_tasks"]
    node_commhub_up_data = commhub_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                  output_var_name=variable_for_tasks.parameterName,
                                                  output_var_type_id=variable_for_tasks.typeId,
                                                  service_id=tech_service.serviceId,
                                                  service_version_id=tech_service.versionId,
                                                  param_id=variable_for_tasks.parameterId)
    update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_commhub_read_without_filters_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def commhub_read_with_client_filter(super_user, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом Выгрузка задач из Communication Hub c настроенным фильтром по
    идентификатору клиента
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение commhub"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="COMMUNICATION_HUB_READ").body[0])
    variable_for_tasks: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_read_tasks"]
    input_var_client_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_comm_client_id"]
    client_type = generate_string(6)
    node_commhub_up_data = commhub_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                  output_var_name=variable_for_tasks.parameterName,
                                                  output_var_type_id=variable_for_tasks.typeId,
                                                  param_id=variable_for_tasks.parameterId,
                                                  service_id=tech_service.serviceId,
                                                  service_version_id=tech_service.versionId,
                                                  client_id_var_name=input_var_client_id.parameterName,
                                                  client_id_type_id=input_var_client_id.typeId,
                                                  client_v_param_id=input_var_client_id.parameterId,
                                                  channel=["SMS"],
                                                  client_id_type=client_type)
    update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_comHub_read_client_filter" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data, "client_type": client_type}


@pytest.fixture()
def commhub_read_with_date_filter(super_user, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом Выгрузка задач из Communication Hub c настроенным фильтром по
    периоду создания записи с предыдущего дня до текущей даты
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение commhub"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="COMMUNICATION_HUB_READ").body[0])
    variable_for_tasks: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_read_tasks"]
    created_before_var = (datetime.datetime.today()).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    created_after_var = str(datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')) + '.000'
    node_commhub_up_data = commhub_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                  output_var_name=variable_for_tasks.parameterName,
                                                  output_var_type_id=variable_for_tasks.typeId,
                                                  param_id=variable_for_tasks.parameterId,
                                                  service_id=tech_service.serviceId,
                                                  service_version_id=tech_service.versionId,
                                                  created_before=created_before_var,
                                                  created_after=created_after_var)
    update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_comHub_read_date_filter" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def commhub_read_with_additional_info(super_user, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом Выгрузка задач из Communication Hub c дополнительной информацией
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение commhub"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="COMMUNICATION_HUB_READ").body[0])
    variable_for_tasks: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_read_tasks"]
    node_commhub_up_data = commhub_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                  output_var_name=variable_for_tasks.parameterName,
                                                  output_var_type_id=variable_for_tasks.typeId,
                                                  param_id=variable_for_tasks.parameterId,
                                                  service_id=tech_service.serviceId,
                                                  service_version_id=tech_service.versionId,
                                                  embed=[EmbedEnum.TASK_STATES])
    update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_comHub_read_ad_info" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}
