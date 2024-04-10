import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, DiagramInOutParameterFullViewDto, \
    NodeViewWithVariablesDto, \
    NodeUpdateDto, DiagramViewDto, ScriptFullView, ScriptVariableFullView, ResponseDto, \
    CommunicationChannelFullViewDto, NodeValidateDto, VariableType1, DataSourceType1, \
    ExternalServiceShortInfoVersionDto, CommunicationVariableFullViewDto
from products.Decision.framework.steps.decision_steps_communication_api import get_communication_channel
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_external_service_api import get_tech_service
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.utilities.commhub_node_constructors import commhub_write_construct
from products.Decision.utilities.communication_constructors import communication_var_construct, communication_construct
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.node_cunstructors import all_node_construct, variables_for_node, \
    comm_node_var_construct, comms_node_construct


@pytest.fixture()
def commhub_write(super_user, create_code_gen, create_communication_gen,
                  diagram_constructor,
                  save_diagrams_gen):
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_commhub_read: NodeViewShortInfo = diagram_constructor["nodes"]["запись commhub"]
    node_comms: NodeViewShortInfo = diagram_constructor["nodes"]["коммуникация"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceShortInfoVersionDto = ExternalServiceShortInfoVersionDto.construct(
        **get_tech_service(super_user, node_type="COMMUNICATION_HUB").body[0])
    variable_for_task: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_task"]
    input_vars_comm_address: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_comm_address"]
    input_vars_comm_channel: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_comm_channel"]
    input_vars_comm_control_group: DiagramInOutParameterFullViewDto = diagram_constructor["variables"][
        "in_comm_control_group"]
    input_vars_comm_ignore_hours: DiagramInOutParameterFullViewDto = diagram_constructor["variables"][
        "in_comm_ignore_hours"]
    input_vars_comm_client_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_comm_client_id"]
    input_vars_comm_client_id_type: DiagramInOutParameterFullViewDto = diagram_constructor["variables"][
        "in_comm_client_id_type"]
    input_vars_comm_priority: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_comm_priority"]
    # СОЗДАНИЕ СКРИПТА ДЛЯ КОММУНИКАЦИИ
    script_inp_var_address = script_vars_construct(
        var_name="in_address",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="2",
    )
    script_inp_var_channel = script_vars_construct(
        var_name="in_channel",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="2",
    )
    script_inp_var_control_group = script_vars_construct(
        var_name="in_controlGroup",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="4",
    )
    script_inp_var_ignore_hours = script_vars_construct(
        var_name="in_ignoreBusinessHour",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="4",
    )
    script_inp_var_client_id = script_vars_construct(
        var_name="in_clientId",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="2",
    )
    script_inp_var_client_id_type = script_vars_construct(
        var_name="in_clientId_type",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="2",
    )
    script_inp_var_priority = script_vars_construct(
        var_name="in_priority",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="2",
    )
    script_out_var = script_vars_construct(
        var_name="out_task",
        var_type=VariableType1.OUT,
        is_array=False,
        complex_vers_id=variable_for_task.typeId,
    )
    script_text = "def template = [:]\ntemplate.text = 'Скидки на товары категории'" \
                  "\n\ndef contactInfo = [:]" \
                  "\ncontactInfo.name = 'Alice'" \
                  "\ncontactInfo.age = '65'" \
                  "\n\ndef properties = [:]" \
                  "\nproperties.discount = '15'" \
                  "\nproperties.category = 'цветы'" \
                  "\n\ndef offer = [:]" \
                  "\noffer.id = 12" \
                  "\n\ndef task = [:]" \
                  f"\ntask.address = {script_inp_var_address.variableName}" \
                  f"\ntask.channel = {script_inp_var_channel.variableName}" \
                  f"\ntask.priority = {script_inp_var_priority.variableName}" \
                  f"\ntask.inControlGroup = {script_inp_var_control_group.variableName}" \
                  f"\ntask.ignoreBusinessHour = {script_inp_var_ignore_hours.variableName}" \
                  f"\ntask.clientId = {script_inp_var_client_id.variableName}" \
                  "\ntask.timeZone = 'UTC'" \
                  "\ntask.template = template" \
                  "\ntask.contactInfo = contactInfo" \
                  "\ntask.properties = properties" \
                  "\ntask.offers = [offer]" \
                  f"\ntask.clientIdType = {script_inp_var_client_id_type.variableName}" \
                  "\ndef root = [:]" \
                  "\nroot.tasks = [task]" \
                  "\nout_task = root"
    # script_text_input = f"\ntask.address = {script_inp_var_address.variableName}" \
    #                     f"\ntask.channel = {script_inp_var_channel.variableName}" \
    #                     f"\ntask.priority = {script_inp_var_priority.variableName}" \
    #                     f"\ntask.inControlGroup = {script_inp_var_control_group.variableName}" \
    #                     f"\ntask.ignoreBusinessHour = {script_inp_var_ignore_hours.variableName}" \
    #                     f"\ntask.clientId = {script_inp_var_client_id.variableName}"
    script_name = "test_groovy_script_for_commhub_write" + generate_string()
    script_data = create_code_gen.create_groovy_code(
        script_text, script_name, variables=[script_inp_var_address, script_inp_var_channel,
                                             script_inp_var_control_group, script_inp_var_ignore_hours,
                                             script_inp_var_client_id, script_inp_var_priority,
                                             script_inp_var_client_id_type, script_out_var]
    )
    script_view: ScriptFullView = script_data["code_create_result"]
    script_inp_var_address_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_inp_var_address.variableName]
    script_inp_var_channel_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_inp_var_channel.variableName]
    script_inp_var_priority_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_inp_var_priority.variableName]
    script_inp_var_control_group_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_inp_var_control_group.variableName]
    script_inp_var_ignore_hours_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_inp_var_ignore_hours.variableName]
    script_inp_var_client_id_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_inp_var_client_id.variableName]
    script_inp_var_client_id_type_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_inp_var_client_id_type.variableName]
    script_out_var_task_with_id: ScriptVariableFullView = script_data["variables_with_ids"][
        script_out_var.variableName]
    # СОЗДАНИЕ КАНАЛА КОММУНИКАЦИИ
    channel_name = "test_channel_for_ch_write" + generate_string()
    channel_var_address = communication_var_construct(
        variable_name="comm_v_addres",
        script_var_name=script_inp_var_address_with_id.variableName,
        primitive_type_id=script_inp_var_address_with_id.primitiveTypeId,
        data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    channel_var_channel = communication_var_construct(
        variable_name="comm_v_channel",
        script_var_name=script_inp_var_channel_with_id.variableName,
        primitive_type_id=script_inp_var_channel_with_id.primitiveTypeId,
        data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    channel_var_priority = communication_var_construct(
        variable_name="comm_v_priority",
        script_var_name=script_inp_var_priority_with_id.variableName,
        primitive_type_id=script_inp_var_priority_with_id.primitiveTypeId,
        data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    channel_var_control_group = communication_var_construct(
        variable_name="comm_v_control_group",
        script_var_name=script_inp_var_control_group_with_id.variableName,
        primitive_type_id=script_inp_var_control_group_with_id.primitiveTypeId,
        data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    channel_var_ignore_hours = communication_var_construct(
        variable_name="comm_v_ignore_hours",
        script_var_name=script_inp_var_ignore_hours_with_id.variableName,
        primitive_type_id=script_inp_var_ignore_hours_with_id.primitiveTypeId,
        data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    channel_var_client_id = communication_var_construct(
        variable_name="comm_v_client_id",
        script_var_name=script_inp_var_client_id_with_id.variableName,
        primitive_type_id=script_inp_var_client_id_with_id.primitiveTypeId,
        data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    channel_var_client_id_type = communication_var_construct(
        variable_name="comm_v_client_id_type",
        script_var_name=script_inp_var_client_id_type_with_id.variableName,
        primitive_type_id=script_inp_var_client_id_type_with_id.primitiveTypeId,
        data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    comm = communication_construct(communication_channel_name=channel_name,
                                   script_version_id=script_view.versionId,
                                   communication_variables=[channel_var_address, channel_var_channel,
                                                            channel_var_priority, channel_var_control_group,
                                                            channel_var_ignore_hours, channel_var_client_id,
                                                            channel_var_client_id_type],
                                   description="made_in_test")
    create_channel_response: ResponseDto = create_communication_gen.create_communication_channel(
        communication_channel_body=comm)
    channel_info = CommunicationChannelFullViewDto(
        **get_communication_channel(super_user, version_id=create_channel_response.uuid).body)
    channel_vars_with_id: dict[str, CommunicationVariableFullViewDto] = {}
    for var in channel_info.communicationVariables:
        channel_vars_with_id[var.variableName] = var
    # ЗАДАНИЕ УЗЛА КОММУНИКАЦИИ
    output_var_mapping = variables_for_node(node_type="comms_out_mapping",
                                            is_arr=variable_for_task.arrayFlag,
                                            is_compl=variable_for_task.complexFlag,
                                            is_dict=variable_for_task.dictFlag,
                                            type_id=variable_for_task.typeId,
                                            node_variable=script_out_var_task_with_id.variableName,
                                            name=variable_for_task.parameterName,
                                            outer_variable_id=script_out_var_task_with_id.variableId)
    node_var_map_address = comm_node_var_construct(var_name=input_vars_comm_address.parameterName,
                                                   var_id=str(
                                                       channel_vars_with_id[channel_var_address.variableName].id),
                                                   type_id=channel_var_address.primitiveTypeId,
                                                   node_variable=channel_var_address.variableName,
                                                   param_id=input_vars_comm_address.parameterId)
    node_var_map_priority = comm_node_var_construct(var_name=input_vars_comm_priority.parameterName,
                                                    var_id=str(
                                                        channel_vars_with_id[channel_var_priority.variableName].id),
                                                    type_id=channel_var_priority.primitiveTypeId,
                                                    node_variable=channel_var_priority.variableName,
                                                    param_id=input_vars_comm_priority.parameterId)
    node_var_map_channel = comm_node_var_construct(var_name=input_vars_comm_channel.parameterName,
                                                   var_id=str(
                                                       channel_vars_with_id[channel_var_channel.variableName].id),
                                                   type_id=channel_var_channel.primitiveTypeId,
                                                   node_variable=channel_var_channel.variableName,
                                                   param_id=input_vars_comm_channel.parameterId)
    node_var_map_control_group = comm_node_var_construct(var_name=input_vars_comm_control_group.parameterName,
                                                         var_id=str(channel_vars_with_id[
                                                                        channel_var_control_group.variableName].id),
                                                         type_id=channel_var_control_group.primitiveTypeId,
                                                         node_variable=channel_var_control_group.variableName,
                                                         param_id=input_vars_comm_control_group.parameterId)
    node_var_map_ignore_hours = comm_node_var_construct(var_name=input_vars_comm_ignore_hours.parameterName,
                                                        var_id=str(channel_vars_with_id[
                                                                       channel_var_ignore_hours.variableName].id),
                                                        type_id=channel_var_ignore_hours.primitiveTypeId,
                                                        node_variable=channel_var_ignore_hours.variableName,
                                                        param_id=input_vars_comm_ignore_hours.parameterId)
    node_var_map_client_id = comm_node_var_construct(var_name=input_vars_comm_client_id.parameterName,
                                                     var_id=str(
                                                         channel_vars_with_id[channel_var_client_id.variableName].id),
                                                     type_id=channel_var_client_id.primitiveTypeId,
                                                     node_variable=channel_var_client_id.variableName,
                                                     param_id=input_vars_comm_client_id.parameterId)
    node_var_map_client_id_type = comm_node_var_construct(var_name=input_vars_comm_client_id_type.parameterName,
                                                          var_id=str(channel_vars_with_id[
                                                                         channel_var_client_id_type.variableName].id),
                                                          type_id=channel_var_client_id_type.primitiveTypeId,
                                                          node_variable=channel_var_client_id_type.variableName,
                                                          param_id=input_vars_comm_client_id_type.parameterId)
    node_comm_up_data = comms_node_construct(chanel_name=channel_info.objectName,
                                             chanel_id=str(channel_info.communicationChannelId),
                                             chanel_vers_id=str(channel_info.versionId),
                                             comms_vars=[],
                                             node_var_mapps=[node_var_map_address, node_var_map_priority,
                                                             node_var_map_channel, node_var_map_control_group,
                                                             node_var_map_ignore_hours, node_var_map_client_id,
                                                             node_var_map_client_id_type],
                                             output_var_mapps=[output_var_mapping])
    comms_update_body = all_node_construct(x=700, y=202.22915649414062,
                                           node_id=str(node_comms.nodeId),
                                           temp_version_id=diagram_constructor["temp_version_id"],
                                           node_name=node_comms.nodeName,
                                           int_node_type=node_comms.nodeTypeId,
                                           properties=node_comm_up_data,
                                           operation="update")
    update_node(super_user, node_id=node_comms.nodeId, body=comms_update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=comms_update_body.nodeTypeId,
                    properties=comms_update_body.properties))
    # ЗАДАНИЕ УЗЛА ЗАПИСИ КОММХАБ
    node_commhub_up_data = commhub_write_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                   input_var_name=variable_for_task.parameterName,
                                                   input_var_type_id=variable_for_task.typeId,
                                                   input_var_id=variable_for_task.parameterId,
                                                   service_id=tech_service.serviceId,
                                                   service_version_id=tech_service.versionId)
    update_node(super_user, node_id=node_commhub_read.nodeId, body=node_commhub_up_data)
    # ПЕРЕСОХРАНЕНИЕ УЗЛА ЗАВЕРШЕНИЯ
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    # СОХРАНЕНИЕ ДИАГРАММЫ
    new_diagram_name = "ag_test_diagram_commhub_write_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}
