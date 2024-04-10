import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import ScriptFullView, ScriptVariableFullView, DataSourceType1, DynamicListType1, \
    ResponseDto, CommunicationChannelFullViewDto, CommunicationVariableFullViewDto, NodeViewShortInfo, \
    DiagramInOutParameterFullViewDto, NodeValidateDto, NodeViewWithVariablesDto, DiagramViewDto, \
    CustomAttributeDictionaryFullView
from products.Decision.framework.steps.decision_steps_communication_api import get_communication_channel
from products.Decision.framework.steps.decision_steps_custom_attr_dict import get_custom_attribute
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.utilities.communication_constructors import communication_var_construct, communication_construct
from products.Decision.utilities.custom_models import IntValueType
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct
from products.Decision.utilities.node_cunstructors import variables_for_node, comm_var_construct, comms_node_construct, \
    all_node_construct, comm_node_var_construct, node_update_construct


@pytest.fixture()
def communication_user_input_diagram_saved(super_user, diagram_constructor, create_communication_gen,
                                           create_groovy_code_int_vars, save_diagrams_gen):
    diagram_id = diagram_constructor["diagram_id"]
    script_view: ScriptFullView = create_groovy_code_int_vars["code_view"]
    script_inp_var: ScriptVariableFullView = create_groovy_code_int_vars["inp_var"]
    script_out_var: ScriptVariableFullView = create_groovy_code_int_vars["out_var"]
    channel_name = "channel_" + generate_string()
    channel_var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=script_inp_var.variableName,
                                              primitive_type_id=script_inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT,
                                              dynamic_list_type=DynamicListType1.DROP_DOWN_LIST
                                              )
    comm = communication_construct(communication_channel_name=channel_name,
                                   script_version_id=script_view.versionId,
                                   communication_variables=[channel_var],
                                   description="made_in_test")

    create_response: ResponseDto = create_communication_gen.create_communication_channel(
        communication_channel_body=comm)
    channel_info = CommunicationChannelFullViewDto(
        **get_communication_channel(super_user, version_id=create_response.uuid).body)
    channel_var: CommunicationVariableFullViewDto = channel_info.communicationVariables[0]
    node_comms: NodeViewShortInfo = diagram_constructor["nodes"]["коммуникация"]
    diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int_v"]
    temp_version_id = diagram_constructor["temp_version_id"]
    output_var_mapping = variables_for_node(node_type="comms_out_mapping",
                                            is_arr=False,
                                            is_compl=False,
                                            is_dict=False,
                                            type_id=diagram_param_out.typeId,
                                            node_variable=script_out_var.variableName,
                                            name=diagram_param_out.parameterName,
                                            outer_variable_id=script_out_var.variableId,
                                            param_id=diagram_param_out.parameterId)
    comms_field = comm_var_construct(var_name=channel_var.variableName,
                                     var_id=str(channel_var.id),
                                     var_value=5,
                                     data_source_type=channel_var.dataSourceType,
                                     dynamic_list_type=channel_var.dynamicListType,
                                     type_id=channel_var.primitiveTypeId,
                                     display_name=channel_var.variableName)
    node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                 chanel_id=str(channel_info.communicationChannelId),
                                                 chanel_vers_id=str(channel_info.versionId),
                                                 comms_vars=[comms_field],
                                                 output_var_mapps=[output_var_mapping])
    update_body = all_node_construct(x=700, y=202.22915649414062,
                                     node_id=str(node_comms.nodeId),
                                     temp_version_id=temp_version_id,
                                     node_name=node_comms.nodeName,
                                     int_node_type=node_comms.nodeTypeId,
                                     properties=node_comms_properties,
                                     operation="update")
    update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=update_body.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_comms.nodeId).body)
    new_diagram_name = "ag_test_diagram_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def communication_diagram_element_saved(super_user, diagram_constructor, create_communication_gen,
                                        create_groovy_code_int_vars, save_diagrams_gen):
    diagram_id = diagram_constructor["diagram_id"]
    script_view: ScriptFullView = create_groovy_code_int_vars["code_view"]
    script_inp_var: ScriptVariableFullView = create_groovy_code_int_vars["inp_var"]
    script_out_var: ScriptVariableFullView = create_groovy_code_int_vars["out_var"]
    channel_name = "channel_" + generate_string()
    channel_var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=script_inp_var.variableName,
                                              primitive_type_id=script_inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
    comm = communication_construct(communication_channel_name=channel_name,
                                   script_version_id=script_view.versionId,
                                   communication_variables=[channel_var],
                                   description="made_in_test")

    create_response: ResponseDto = create_communication_gen.create_communication_channel(
        communication_channel_body=comm)
    channel_info = CommunicationChannelFullViewDto(
        **get_communication_channel(super_user, version_id=create_response.uuid).body)
    channel_var: CommunicationVariableFullViewDto = channel_info.communicationVariables[0]
    node_comms: NodeViewShortInfo = diagram_constructor["nodes"]["коммуникация"]
    diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int_v"]
    diagram_param_in: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_v"]
    temp_version_id = diagram_constructor["temp_version_id"]
    output_var_mapping = variables_for_node(node_type="comms_out_mapping",
                                            is_arr=False,
                                            is_compl=False,
                                            is_dict=False,
                                            type_id=diagram_param_out.typeId,
                                            node_variable=script_out_var.variableName,
                                            name=diagram_param_out.parameterName,
                                            outer_variable_id=script_out_var.variableId,
                                            param_id=diagram_param_out.parameterId)
    node_var_map = comm_node_var_construct(var_name=diagram_param_in.parameterName,
                                           var_id=str(channel_var.id),
                                           type_id=channel_var.primitiveTypeId,
                                           param_id=diagram_param_in.parameterId,
                                           node_variable=channel_var.variableName)
    node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                 chanel_id=str(channel_info.communicationChannelId),
                                                 chanel_vers_id=str(channel_info.versionId),
                                                 comms_vars=[],
                                                 node_var_mapps=[node_var_map],
                                                 output_var_mapps=[output_var_mapping])
    update_body = all_node_construct(x=700, y=202.22915649414062,
                                     node_id=str(node_comms.nodeId),
                                     temp_version_id=temp_version_id,
                                     node_name=node_comms.nodeName,
                                     int_node_type=node_comms.nodeTypeId,
                                     properties=node_comms_properties,
                                     operation="update")
    update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=update_body.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_comms.nodeId).body)
    new_diagram_name = "ag_test_diagram_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def communication_dict_diagram_saved(super_user, diagram_constructor, create_dict_gen, create_groovy_code_int_vars,
                                     create_communication_gen, save_diagrams_gen):
    diagram_id = diagram_constructor["diagram_id"]
    script_view: ScriptFullView = create_groovy_code_int_vars["code_view"]
    script_inp_var: ScriptVariableFullView = create_groovy_code_int_vars["inp_var"]
    script_out_var: ScriptVariableFullView = create_groovy_code_int_vars["out_var"]
    value = dict_value_construct(dict_value="15",
                                 dict_value_display_name="")
    custom_attr = dict_construct(
        dict_name="ag_test_dict" + generate_string(),
        dict_value_type_id="1",
        values=[value])
    create_result_dict: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
    dict_attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
        **get_custom_attribute(super_user, dict_id=create_result_dict.uuid).body)
    channel_name = "channel_" + generate_string()
    channel_var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=script_inp_var.variableName,
                                              primitive_type_id=script_inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.DICTIONARY,
                                              dynamic_list_type=DynamicListType1.DROP_DOWN_LIST,
                                              dict_id=create_result_dict.uuid)
    comm = communication_construct(communication_channel_name=channel_name,
                                   script_version_id=script_view.versionId,
                                   communication_variables=[channel_var],
                                   description="made_in_test")

    create_response: ResponseDto = create_communication_gen.create_communication_channel(
        communication_channel_body=comm)
    channel_info = CommunicationChannelFullViewDto(
        **get_communication_channel(super_user, version_id=create_response.uuid).body)
    channel_var: CommunicationVariableFullViewDto = channel_info.communicationVariables[0]
    node_comms: NodeViewShortInfo = diagram_constructor["nodes"]["коммуникация"]
    diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int_v"]
    temp_version_id = diagram_constructor["temp_version_id"]
    output_var_mapping = variables_for_node(node_type="comms_out_mapping",
                                            is_arr=False,
                                            is_compl=False,
                                            is_dict=False,
                                            type_id=diagram_param_out.typeId,
                                            node_variable=script_out_var.variableName,
                                            name=diagram_param_out.parameterName,
                                            outer_variable_id=script_out_var.variableId,
                                            param_id=diagram_param_out.parameterId)
    comms_field = comm_var_construct(var_name=channel_var.variableName,
                                     var_id=str(channel_var.id),
                                     var_value=dict_attr_info.values[0]["dictValue"],
                                     data_source_type=channel_var.dataSourceType,
                                     dynamic_list_type=channel_var.dynamicListType,
                                     type_id=channel_var.primitiveTypeId,
                                     display_name=channel_var.variableName)
    node_var_map = comm_node_var_construct(var_name="in_int_v",
                                           var_id=str(channel_var.id),
                                           type_id=channel_var.primitiveTypeId,
                                           node_variable=channel_var.variableName)
    node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                 chanel_id=str(channel_info.communicationChannelId),
                                                 chanel_vers_id=str(channel_info.versionId),
                                                 comms_vars=[comms_field],
                                                 output_var_mapps=[output_var_mapping])
    update_body = all_node_construct(x=700, y=202.22915649414062,
                                     node_id=str(node_comms.nodeId),
                                     temp_version_id=temp_version_id,
                                     node_name=node_comms.nodeName,
                                     int_node_type=node_comms.nodeTypeId,
                                     properties=node_comms_properties,
                                     operation="update")
    update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=update_body.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_comms.nodeId).body)
    new_diagram_name = "ag_test_diagram_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def communication_node_var_diagram_saved(super_user, diagram_constructor, create_communication_gen,
                                         create_groovy_code_int_vars, save_diagrams_gen):
    diagram_id = diagram_constructor["diagram_id"]
    script_view: ScriptFullView = create_groovy_code_int_vars["code_view"]
    script_inp_var: ScriptVariableFullView = create_groovy_code_int_vars["inp_var"]
    script_out_var: ScriptVariableFullView = create_groovy_code_int_vars["out_var"]
    channel_name = "channel_" + generate_string()
    channel_var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=script_inp_var.variableName,
                                              primitive_type_id=script_inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT,
                                              dynamic_list_type=DynamicListType1.DROP_DOWN_LIST
                                              )
    comm = communication_construct(communication_channel_name=channel_name,
                                   script_version_id=script_view.versionId,
                                   communication_variables=[channel_var],
                                   description="made_in_test")

    create_response: ResponseDto = create_communication_gen.create_communication_channel(
        communication_channel_body=comm)
    channel_info = CommunicationChannelFullViewDto(
        **get_communication_channel(super_user, version_id=create_response.uuid).body)
    channel_var: CommunicationVariableFullViewDto = channel_info.communicationVariables[0]
    node_comms: NodeViewShortInfo = diagram_constructor["nodes"]["коммуникация"]
    diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int_v"]
    diagram_param_in: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_v"]
    temp_version_id = diagram_constructor["temp_version_id"]
    output_var_mapping = variables_for_node(node_type="comms_out_mapping",
                                            is_arr=False,
                                            is_compl=False,
                                            is_dict=False,
                                            type_id=diagram_param_out.typeId,
                                            node_variable=script_out_var.variableName,
                                            name=diagram_param_out.parameterName,
                                            outer_variable_id=script_out_var.variableId)
    comms_field = comm_var_construct(var_name=channel_var.variableName,
                                     var_id=str(channel_var.id),
                                     var_value=5,
                                     data_source_type=channel_var.dataSourceType,
                                     dynamic_list_type=channel_var.dynamicListType,
                                     type_id=channel_var.primitiveTypeId,
                                     display_name=channel_var.variableName)
    node_var_map = comm_node_var_construct(var_name=diagram_param_in.parameterName,
                                           var_id=None,
                                           type_id=diagram_param_out.typeId,
                                           node_variable="node_var",
                                           is_variable_from_channel_template=False)
    node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                 chanel_id=str(channel_info.communicationChannelId),
                                                 chanel_vers_id=str(channel_info.versionId),
                                                 comms_vars=[comms_field],
                                                 node_var_mapps=[node_var_map],
                                                 output_var_mapps=[output_var_mapping])
    update_body = all_node_construct(x=700, y=202.22915649414062,
                                     node_id=str(node_comms.nodeId),
                                     temp_version_id=temp_version_id,
                                     node_name=node_comms.nodeName,
                                     int_node_type=node_comms.nodeTypeId,
                                     properties=node_comms_properties,
                                     operation="update")
    update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=update_body.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_comms.nodeId).body)
    new_diagram_name = "ag_test_diagram_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def communication_consts_diagram_empty_node(super_user, custom_code_communication, create_communication_gen,
                                            diagram_constructor):
    with allure.step("Создание пользовательского кода"):
        diagram_id = diagram_constructor["diagram_id"]
        script_view: ScriptFullView = custom_code_communication["code_view"]
        script_inp_date_time_var: ScriptVariableFullView = custom_code_communication["inp_date_time_var"]
        script_inp_time_var: ScriptVariableFullView = custom_code_communication["inp_time_var"]
        script_inp_str_var: ScriptVariableFullView = custom_code_communication["inp_str_restrict_var"]
        script_inp_long_var: ScriptVariableFullView = custom_code_communication["inp_long_var_us_input"]
        script_inp_str_dict_var: ScriptVariableFullView = custom_code_communication["inp_str_dict_var"]
        script_inp_bool_var: ScriptVariableFullView = custom_code_communication["inp_bool_var"]
        script_inp_date_var: ScriptVariableFullView = custom_code_communication["inp_date_var"]
        script_inp_double_var: ScriptVariableFullView = custom_code_communication["inp_double_restrict_var"]
        script_inp_int_dict_var: ScriptVariableFullView = custom_code_communication["inp_int_dict_var"]
        script_out_date_time_var: ScriptVariableFullView = custom_code_communication["out_date_time_var"]
        script_out_date_var: ScriptVariableFullView = custom_code_communication["out_date_var"]
        script_out_bool_var: ScriptVariableFullView = custom_code_communication["out_bool_var"]
        script_out_time_var: ScriptVariableFullView = custom_code_communication["out_time_var"]
        script_inout_var_with_id: ScriptVariableFullView = custom_code_communication["inout_var_with_id"]
        channel_name = "channel_" + generate_string()
        script_out_vars = [script_out_date_time_var, script_out_date_var, script_out_bool_var, script_out_time_var]
    with allure.step("Задание параметров канала коммуникаций"):
        channel_name = "channel_" + generate_string()
        channel_var_date_time = communication_var_construct(variable_name="comm_inp_date_time_var",
                                                            script_var_name=script_inp_date_time_var.variableName,
                                                            primitive_type_id=script_inp_date_time_var.primitiveTypeId,
                                                            data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_time = communication_var_construct(variable_name="comm_inp_time_var",
                                                       script_var_name=script_inp_time_var.variableName,
                                                       primitive_type_id=script_inp_time_var.primitiveTypeId,
                                                       data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_str = communication_var_construct(variable_name="comm_inp_str_var",
                                                      script_var_name=script_inp_str_var.variableName,
                                                      primitive_type_id=script_inp_str_var.primitiveTypeId,
                                                      data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_long = communication_var_construct(variable_name="comm_inp_long_var",
                                                       script_var_name=script_inp_long_var.variableName,
                                                       primitive_type_id=script_inp_long_var.primitiveTypeId,
                                                       data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_str_dict = communication_var_construct(variable_name="comm_inp_str_dict_var",
                                                           script_var_name=script_inp_str_dict_var.variableName,
                                                           primitive_type_id=script_inp_str_dict_var.primitiveTypeId,
                                                           data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_bool = communication_var_construct(variable_name="comm_inp_bool_var",
                                                       script_var_name=script_inp_bool_var.variableName,
                                                       primitive_type_id=script_inp_bool_var.primitiveTypeId,
                                                       data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_date = communication_var_construct(variable_name="comm_inp_date_var",
                                                       script_var_name=script_inp_date_var.variableName,
                                                       primitive_type_id=script_inp_date_var.primitiveTypeId,
                                                       data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_double = communication_var_construct(variable_name="comm_inp_double_var",
                                                         script_var_name=script_inp_double_var.variableName,
                                                         primitive_type_id=script_inp_double_var.primitiveTypeId,
                                                         data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        channel_var_int_dict = communication_var_construct(variable_name="comm_inp_int_dict_var",
                                                           script_var_name=script_inp_int_dict_var.variableName,
                                                           primitive_type_id=script_inp_int_dict_var.primitiveTypeId,
                                                           data_source_type=DataSourceType1.DIAGRAM_ELEMENT)
        comm = communication_construct(communication_channel_name=channel_name,
                                       script_version_id=script_view.versionId,
                                       communication_variables=[channel_var_long, channel_var_str,
                                                                channel_var_time, channel_var_date_time,
                                                                channel_var_int_dict, channel_var_double,
                                                                channel_var_date, channel_var_bool,
                                                                channel_var_str_dict],
                                       description="made_in_test")
    with allure.step("Создание канала коммуникаций"):
        create_response: ResponseDto = create_communication_gen.create_communication_channel(
            communication_channel_body=comm)
    with allure.step("Поиск канала коммуникаций по идентификатору версии"):
        channel_info = CommunicationChannelFullViewDto(
            **get_communication_channel(super_user, version_id=create_response.uuid).body)
        channel_var_date_time_with_id: CommunicationVariableFullViewDto = None
        channel_var_time_with_id: CommunicationVariableFullViewDto = None
        channel_var_str_with_id: CommunicationVariableFullViewDto = None
        channel_var_long_with_id: CommunicationVariableFullViewDto = None
        channel_var_str_dict_with_id: CommunicationVariableFullViewDto = None
        channel_var_bool_with_id: CommunicationVariableFullViewDto = None
        channel_var_date_with_id: CommunicationVariableFullViewDto = None
        channel_var_double_with_id: CommunicationVariableFullViewDto = None
        channel_var_int_dict_with_id: CommunicationVariableFullViewDto = None
        channel_vars = []
        for var in channel_info.communicationVariables:
            channel_vars.append(var)
            if var.variableName == "comm_inp_int_dict_var":
                channel_var_int_dict_with_id = var
            elif var.variableName == "comm_inp_date_var":
                channel_var_date_with_id = var
            elif var.variableName == "comm_inp_bool_var":
                channel_var_bool_with_id = var
            elif var.variableName == "comm_inp_long_var":
                channel_var_long_with_id = var
            elif var.variableName == "comm_inp_str_var":
                channel_var_str_with_id = var
            elif var.variableName == "comm_inp_str_dict_var":
                channel_var_str_dict_with_id = var
            elif var.variableName == "comm_inp_double_var":
                channel_var_double_with_id = var
            elif var.variableName == "comm_inp_time_var":
                channel_var_time_with_id = var
            elif var.variableName == "comm_inp_date_time_var":
                channel_var_date_time_with_id = var

    return {"diagram_id": diagram_id, "nodes": diagram_constructor["nodes"],
            "variables": diagram_constructor["variables"], "temp_version_id": diagram_constructor["temp_version_id"],
            "channel_info": channel_info,
            "script_info": script_view,
            "channel_var_date_time_with_id": channel_var_date_time_with_id,
            "channel_var_time_with_id": channel_var_time_with_id,
            "channel_var_str_with_id": channel_var_str_with_id,
            "channel_var_long_with_id": channel_var_long_with_id,
            "channel_var_str_dict_with_id": channel_var_str_dict_with_id,
            "channel_var_bool_with_id": channel_var_bool_with_id,
            "channel_var_date_with_id": channel_var_date_with_id,
            "channel_var_double_with_id": channel_var_double_with_id,
            "channel_var_int_dict_with_id": channel_var_int_dict_with_id,
            "script_out_date_time_var": script_out_date_time_var,
            "script_out_date_var": script_out_date_var,
            "script_out_bool_var": script_out_bool_var,
            "script_out_time_var": script_out_time_var,
            "script_out_vars": script_out_vars,
            "channel_vars": channel_vars}


@pytest.fixture()
def saved_communication_consts_diagram_empty_node(super_user, communication_consts_diagram_empty_node,
                                                  save_diagrams_gen):
    diagram_id = communication_consts_diagram_empty_node["diagram_id"]
    channel_vars: list[CommunicationVariableFullViewDto] = communication_consts_diagram_empty_node["channel_vars"]
    script_out_vars: list[ScriptVariableFullView] = communication_consts_diagram_empty_node["script_out_vars"]

    node_comms: NodeViewShortInfo = communication_consts_diagram_empty_node["nodes"]["коммуникация"]
    node_end: NodeViewShortInfo = communication_consts_diagram_empty_node["nodes"]["завершение"]
    channel_info: CommunicationChannelFullViewDto = communication_consts_diagram_empty_node["channel_info"]
    diagram_param_out_bool: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
        "variables"]["out1"]
    diagram_param_out_date: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
        "variables"]["out2"]
    diagram_param_out_time: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
        "variables"]["out3"]
    diagram_param_out_date_time: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
        "variables"]["out4"]
    diagram_vars = [diagram_param_out_bool, diagram_param_out_date, diagram_param_out_time,
                    diagram_param_out_date_time]
    temp_version_id = communication_consts_diagram_empty_node["temp_version_id"]

    with allure.step("Обновление узла коммуникации"):

        out_v_map = []
        for script_v in script_out_vars:
            for diagram_v in diagram_vars:
                if diagram_v.typeId == script_v.primitiveTypeId:
                    out_v_map.append(variables_for_node(node_type="comms_out_mapping",
                                                        is_arr=False,
                                                        is_compl=False,
                                                        is_dict=False,
                                                        type_id=diagram_v.typeId,
                                                        node_variable=script_v.variableName,
                                                        name=diagram_v.parameterName,
                                                        outer_variable_id=script_v.variableId,
                                                        param_id=diagram_v.parameterId))
                    break

        comms_map = []
        for comms_v in channel_vars:
            var_name = ""
            if comms_v.primitiveTypeId == IntValueType.float.value:
                var_name = "9.1"
            elif comms_v.primitiveTypeId == IntValueType.int.value:
                var_name = "666"
            elif comms_v.primitiveTypeId == IntValueType.str.value:
                var_name = "'line'"
            elif comms_v.primitiveTypeId == IntValueType.bool.value:
                var_name = "'true'"
            elif comms_v.primitiveTypeId == IntValueType.date.value:
                var_name = "'2023-12-22'"
            elif comms_v.primitiveTypeId == IntValueType.dateTime.value:
                var_name = "'2023-12-22 01:01:01.434'"
            elif comms_v.primitiveTypeId == IntValueType.time.value:
                var_name = "'01:01:01'"
            elif comms_v.primitiveTypeId == IntValueType.long.value:
                var_name = "7"
            comms_map.append(comm_node_var_construct(var_name=var_name,
                                                     var_id=str(comms_v.id),
                                                     type_id=comms_v.primitiveTypeId,
                                                     param_id=None,
                                                     is_literal=True,
                                                     node_variable=comms_v.variableName))
        node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                     chanel_id=str(channel_info.communicationChannelId),
                                                     chanel_vers_id=str(channel_info.versionId),
                                                     comms_vars=[],
                                                     node_var_mapps=comms_map,
                                                     output_var_mapps=out_v_map)
        update_body = all_node_construct(x=700, y=202.22915649414062,
                                         node_id=str(node_comms.nodeId),
                                         temp_version_id=temp_version_id,
                                         node_name=node_comms.nodeName,
                                         int_node_type=node_comms.nodeTypeId,
                                         properties=node_comms_properties,
                                         operation="update")
        update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=update_body.nodeTypeId,
                        properties=update_body.properties))
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_comms.nodeId).body)
    with allure.step("Обновление узла Завершения"):
        finish_variables_bool = variables_for_node(node_type="finish_out", is_arr=diagram_param_out_bool.arrayFlag,
                                                   is_compl=diagram_param_out_bool.complexFlag,
                                                   name=diagram_param_out_bool.parameterName, type_id=diagram_param_out_bool.typeId,
                                                   vers_id=diagram_param_out_bool.parameterVersionId,
                                                   param_name=diagram_param_out_bool.parameterName)
        finish_variables_date = variables_for_node(node_type="finish_out", is_arr=diagram_param_out_date.arrayFlag,
                                                   is_compl=diagram_param_out_date.complexFlag,
                                                   name=diagram_param_out_date.parameterName, type_id=diagram_param_out_date.typeId,
                                                   vers_id=diagram_param_out_date.parameterVersionId,
                                                   param_name=diagram_param_out_date.parameterName)
        finish_variables_time = variables_for_node(node_type="finish_out", is_arr=diagram_param_out_time.arrayFlag,
                                                   is_compl=diagram_param_out_time.complexFlag,
                                                   name=diagram_param_out_time.parameterName, type_id=diagram_param_out_time.typeId,
                                                   vers_id=diagram_param_out_time.parameterVersionId,
                                                   param_name=diagram_param_out_time.parameterName)
        finish_variables_date_time = variables_for_node(node_type="finish_out",
                                                        is_arr=diagram_param_out_date_time.arrayFlag,
                                                        is_compl=diagram_param_out_date_time.complexFlag,
                                                        name=diagram_param_out_date_time.parameterName,
                                                        type_id=diagram_param_out_date_time.typeId,
                                                        vers_id=diagram_param_out_date_time.parameterVersionId,
                                                        param_name=diagram_param_out_date_time.parameterName)
        finish_up_body = node_update_construct(x=1400, y=202,
                                               temp_version_id=temp_version_id,
                                               node_type="finish",
                                               variables=[finish_variables_date_time, finish_variables_time,
                                                          finish_variables_date, finish_variables_bool])
        update_node(super_user, node_id=node_end.nodeId, body=finish_up_body)
        new_diagram_name = "ag_test_diagram_" + generate_string()
        diagram_description = "diagram created in test"
        create_result = save_diagrams_gen.save_diagram(
            diagram_id, temp_version_id, new_diagram_name, diagram_description
        ).body
        saved_version_id = create_result["uuid"]
        save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
            super_user, saved_version_id).body)
        return {"diagram_name": new_diagram_name, "diagram_data": save_data}
