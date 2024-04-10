import random
import string

import pytest

from common.generators import generate_string
from config import settings
from products.Decision.framework.model import DiagramViewDto, ResponseDto, ScriptFullView, \
    NodeViewWithVariablesDto, DiagramCreateNewVersion, ScriptType2, VariableType1, \
    DiagramInOutParametersViewDto, ServiceType, VariableType2, Protocol, SyncType, FileFormat, Method, \
    ExternalServiceFullViewDto, ScriptVariableFullView, \
    SourceType, DataProviderGetFullView, TablesDto, ColumnsDto, ConnectionType
from products.Decision.framework.steps.decision_steps_data_provider_api import get_data_provider, \
    get_data_provider_tables, get_data_provider_table
from products.Decision.framework.steps.decision_steps_diagram import update_diagram_parameters, save_diagram, \
    delete_diagram, create_template, delete_diagram_template
from products.Decision.framework.steps.decision_steps_external_service_api import find_service_by_id
from products.Decision.framework.steps.decision_steps_nodes import create_node, create_link, update_node, get_node_by_id
from products.Decision.framework.steps.decision_steps_script_api import delete_script_by_id, get_groovy_script_by_id, \
    create_groovy_script
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.custom_code_constructors import code_construct, script_vars_construct
from products.Decision.utilities.custom_type_constructors import generate_attr_type_name, attribute_construct
from products.Decision.utilities.data_provider_constructors import provider_setting_construct, data_provider_construct
from products.Decision.utilities.external_service_constructors import service_setting_construct, \
    service_header_construct, service_var_construct, rnd_service_str, service_construct
from products.Decision.utilities.node_cunstructors import *
from products.Decision.utilities.variable_constructors import *


@pytest.fixture()
def diagram_fork_join(super_user,
                      create_temp_diagram_gen):
    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    param_name = "diagram_variable"
    parameter_version_id2 = str(uuid.uuid4())
    new_var = variable_construct(array_flag=False,
                                 complex_flag=False,
                                 default_value=None,
                                 is_execute_status=None,
                                 order_num=0,
                                 param_name=param_name,
                                 parameter_type="in_out",
                                 parameter_version_id=parameter_version_id2,
                                 type_id=1,
                                 parameter_id=parameter_version_id2)
    params_response = update_diagram_parameters(super_user, temp_version_id, [diagram_exec_var, new_var])
    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node("start", False, False, param_name, 1, parameter_version_id2,
                                         None, None, None, None)
    finish_variables = variables_for_node("finish", False, False, param_name, 1, parameter_version_id2,
                                          None, None, None, None)

    node_start_raw = node_construct(-183, 246, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(1128, 721, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    node_fork = fork_node_construct(x=304,
                                    y=246,
                                    temp_version_id=temp_version_id,
                                    branches=None)
    node_fork_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_fork).body)
    node_fork_id = node_fork_response.uuid

    node_calc1 = node_construct(x=777,
                                y=446,
                                node_type="var_calc",
                                temp_version_id=temp_version_id,
                                variables=None)
    node_calc1_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_calc1).body)
    node_calc1_id = node_calc1_response.uuid

    node_calc2 = node_construct(x=777,
                                y=46,
                                node_type="var_calc",
                                temp_version_id=temp_version_id,
                                variables=None)
    node_calc2_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_calc2).body)
    node_calc2_id = node_calc2_response.uuid

    node_join = join_node_construct(x=1200,
                                    y=246,
                                    temp_version_id=temp_version_id,
                                    branches=None)
    node_join_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_join).body)
    node_join_id = node_join_response.uuid

    link_s_f = link_construct(temp_version_id, node_start.uuid, node_fork_id)
    link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
    link_s_f_id = link_s_f_create_response.uuid

    link_f_c1 = link_construct(temp_version_id, node_fork_id, node_calc1_id)
    link_f_c1_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_f_c1).body)
    link_f_c1_id = link_f_c1_create_response.uuid

    link_f_c2 = link_construct(temp_version_id, node_fork_id, node_calc2_id)
    link_f_c2_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_f_c2).body)
    link_f_c2_id = link_f_c2_create_response.uuid

    link_c1_j = link_construct(temp_version_id, node_calc1_id, node_join_id)
    link_c1_j_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_c1_j).body)
    link_c1_j_id = link_c1_j_create_response.uuid

    link_c2_j = link_construct(temp_version_id, node_calc2_id, node_join_id)
    link_c2_j_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_c2_j).body)
    link_c2_j_id = link_c2_j_create_response.uuid

    link_j_e = link_construct(temp_version_id, node_join_id, node_end.uuid)
    link_j_e_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_j_e).body)
    link_j_e_id = link_j_e_create_response.uuid

    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)

    return {"diagram_template": diagram_template,
            "node_fork_id": node_fork_id,
            "node_join_id": node_join_id,
            "node_calc1_id": node_calc1_id,
            "node_calc2_id": node_calc2_id,
            "link_s_f_id": link_s_f_id,
            "link_f_c1_id": link_f_c1_id,
            "link_f_c2_id": link_f_c2_id,
            "link_c1_j_id": link_c1_j_id,
            "link_c2_j_id": link_c2_j_id,
            "link_j_e_id": link_j_e_id,
            "diagram_variable": new_var,
            "node_end_id": node_end.uuid}


@pytest.fixture()
def diagram_ruleset(super_user,
                    create_custom_types_gen,
                    create_temp_diagram_gen):
    type_name = generate_attr_type_name(True, False, True, "")
    attr = attribute_construct()
    create_result: ResponseDto = create_custom_types_gen.create_type(type_name, [attr])
    custom_type_version_id = create_result.uuid

    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    param_name = "diagram_variable"
    parameter_version_id = str(uuid.uuid4())
    new_var = variable_construct(array_flag=False,
                                 complex_flag=True,
                                 default_value=None,
                                 is_execute_status=None,
                                 order_num=0,
                                 param_name=param_name,
                                 parameter_type="in_out",
                                 parameter_version_id=parameter_version_id,
                                 type_id=custom_type_version_id)
    params_response = update_diagram_parameters(super_user, temp_version_id, [diagram_exec_var, new_var])
    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node(node_type="start",
                                         is_arr=False,
                                         is_compl=True,
                                         name=param_name,
                                         type_id=custom_type_version_id,
                                         vers_id=parameter_version_id)
    finish_variables = variables_for_node(node_type="finish",
                                          is_arr=False,
                                          is_compl=True,
                                          name=param_name,
                                          type_id=custom_type_version_id,
                                          vers_id=parameter_version_id)

    node_start_raw = node_construct(-183, 246, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(1128, 721, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    node_rule = ruleset_node_construct(x=700, y=202.22915649414062, temp_version_id=temp_version_id)
    node_rule_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_rule).body)
    node_rule_id = node_rule_response.uuid

    link_s_r = link_construct(temp_version_id, node_start.uuid, node_rule_id)
    link_s_r_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_r).body)
    link_s_r_id = link_s_r_create_response.uuid

    link_r_e = link_construct(temp_version_id, node_rule_id, node_end.uuid)
    link_r_e_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_r_e).body)
    link_r_e_id = link_r_e_create_response.uuid
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)

    return {"diagram_template": diagram_template,
            "node_rule_id": node_rule_id,
            "diagram_variable": new_var,
            "complex_type_version_id": custom_type_version_id,
            "ctype_attr": attr}


@pytest.fixture()
def diagram_external_service(super_user, create_temp_diagram_gen, get_env, create_service_gen):
    env_id = get_env.get_env_id("default_dev")

    setting = service_setting_construct(environment_settings_id=env_id,
                                        host="some_host",
                                        service_type=ServiceType.HTTPS,
                                        endpoint="/endpoint",
                                        port=443,
                                        second_attempts_cnt=4,
                                        transactions_per_second=3,
                                        interval=3,
                                        timeout=2)

    header = service_header_construct(header_name="test", header_value="\"test\"")

    var_in = service_var_construct(variable_name="var_in",
                                   variable_type=VariableType2.IN,
                                   array_flag=False,
                                   primitive_type_id="1",
                                   complex_type_version_id=None,
                                   source_path="/",
                                   expression=None)

    var_out = service_var_construct(variable_name="var_out",
                                    variable_type=VariableType2.OUT,
                                    array_flag=False,
                                    primitive_type_id="1",
                                    complex_type_version_id=None,
                                    source_path="/path_to_service",
                                    expression=None)

    var_calc = service_var_construct(variable_name="var_calc",
                                     variable_type=VariableType2.CALCULATED,
                                     array_flag=False,
                                     primitive_type_id="1",
                                     complex_type_version_id=None,
                                     source_path="/",
                                     expression="1+1")
    service_name = "service_" + rnd_service_str(8)
    service = service_construct(protocol=Protocol.REST,
                                sync_type=SyncType.SYNC,
                                service_name=service_name,
                                batch_flag=False,
                                description=None,
                                file_format=FileFormat.JSON,
                                method=Method.POST,
                                body="{\"param\":${var_in}\n}",
                                service_settings=[setting],
                                headers=[header],
                                variables=[var_in, var_out, var_calc])

    create_response: ResponseDto = create_service_gen.create_service(service)

    service: ExternalServiceFullViewDto = ExternalServiceFullViewDto.construct(
        **find_service_by_id(super_user, create_response.uuid).body)

    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    param_name = "diagram_variable"
    parameter_version_id = str(uuid.uuid4())
    new_var = variable_construct(array_flag=False,
                                 complex_flag=False,
                                 default_value=None,
                                 is_execute_status=None,
                                 order_num=0,
                                 param_name=param_name,
                                 parameter_type="in_out",
                                 parameter_version_id=parameter_version_id,
                                 parameter_id=parameter_version_id,
                                 type_id=1
                                 )
    params_response = update_diagram_parameters(super_user, str(temp_version_id), [diagram_exec_var, new_var])
    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node(node_type="start",
                                         is_arr=False,
                                         is_compl=False,
                                         name=param_name,
                                         type_id=1,
                                         vers_id=parameter_version_id)
    finish_variables = variables_for_node(node_type="finish",
                                          is_arr=False,
                                          is_compl=False,
                                          name=param_name,
                                          type_id=1,
                                          vers_id=parameter_version_id)

    node_start_raw = node_construct(-183, 246, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(1128, 721, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    node_ext_serv = external_service_node_construct(x=700, y=202.22915649414062, temp_version_id=temp_version_id)
    node_ext_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_ext_serv).body)
    node_ext_id = node_ext_response.uuid

    link_s_e = link_construct(temp_version_id, node_start.uuid, node_ext_id)
    link_s_e_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_e).body)
    link_s_e_id = link_s_e_create_response.uuid

    link_e_f = link_construct(temp_version_id, node_ext_id, node_end.uuid)
    link_e_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_e_f).body)
    link_e_f_id = link_e_f_create_response.uuid
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)

    return {"diagram_template": diagram_template,
            "node_ext_id": node_ext_id,
            "diagram_variable": new_var,
            "external_service": service}


@pytest.fixture(scope="class")
def diagram_custom_code_submit(super_user):
    inp_var = script_vars_construct(var_name="input_int",
                                    var_type=VariableType1.IN,
                                    is_array=False, primitive_id="1")
    out_var = script_vars_construct(var_name="output_int",
                                    var_type=VariableType1.OUT,
                                    is_array=False, primitive_id="1")
    script_text = "output_int = input_int + 2"
    script_name = "test_groovy_script_" + generate_diagram_name_description(6, 1)["rand_name"]
    script = code_construct(script_type="groovy",
                            script_name=script_name,
                            script_text=script_text,
                            variables=[inp_var, out_var])
    groovy_code_create_result = ScriptFullView.construct(**create_groovy_script(super_user, body=script).body)
    script_view = ScriptFullView.construct(
        **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
    input_var_with_id = None
    output_var_with_id = None
    variables = []
    for var in script_view.variables:
        variables.append(ScriptVariableFullView.construct(**var))
    for var in variables:
        if var.variableType == "IN":
            input_var_with_id = var
        if var.variableType == "OUT":
            output_var_with_id = var

    response_create_template = create_template(super_user)
    template = response_create_template.body
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **template["inOutParameters"][0])
    temp_version_id = template["versionId"]

    param_name = "diagram_variable"
    parameter_version_id2 = str(uuid.uuid4())
    new_var = variable_construct(array_flag=False,
                                 complex_flag=False,
                                 default_value=None,
                                 is_execute_status=None,
                                 order_num=0,
                                 param_name=param_name,
                                 parameter_type="in_out",
                                 parameter_version_id=parameter_version_id2,
                                 parameter_id=parameter_version_id2,
                                 type_id=1)
    params_response = update_diagram_parameters(super_user, str(temp_version_id),
                                                [diagram_exec_var, new_var])
    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node("start", False, False, param_name, 1, parameter_version_id2,
                                         None, None, None, None)
    finish_variables = variables_for_node("finish", False, False, param_name, 1, parameter_version_id2,
                                          None, None, None, None)

    node_start_raw = node_construct(-183, 246, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(1128, 721, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    node_script = node_construct(700, 202.22915649414062, "custom_code", temp_version_id)
    node_script_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_script).body)
    node_script_id = node_script_response.uuid

    link_s_c = link_construct(temp_version_id, node_start.uuid, node_script_id)
    link_s_c_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_c).body)
    link_s_c_id = link_s_c_create_response.uuid

    link_c_e = link_construct(temp_version_id, node_script_id, node_end.uuid)
    link_c_e_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_c_e).body)
    link_c_e_id = link_c_e_create_response.uuid

    script_id = script_view.scriptId
    script_version_id = script_view.versionId

    temp_version_id = template["versionId"]
    diagram_id = template["diagramId"]
    out_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=new_var.parameterName,
                                     node_variable=output_var_with_id.variableName,
                                     type_id=out_var.primitiveTypeId,
                                     outer_variable_id=output_var_with_id.variableId,
                                     param_id=new_var.parameterId)
    inp_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=new_var.parameterName,
                                     node_variable=input_var_with_id.variableName,
                                     type_id=inp_var.primitiveTypeId,
                                     outer_variable_id=input_var_with_id.variableId,
                                     param_id=new_var.parameterId)
    node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                            temp_version_id=temp_version_id,
                                            script_id=script_id, script_version_id=script_version_id,
                                            script_type=ScriptType2.GROOVY,
                                            inp_custom_code_vars=[inp_var_map], out_custom_code_vars=[out_var_map])
    update_node_response = update_node(super_user,
                                       node_id=node_script_id,
                                       body=node_script_upd)
    script_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_script_id).body)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)

    new_diagram_name = "diagram" + "_" + generate_diagram_name_description(6, 1)["rand_name"]
    diagram_description = 'diagram created in test'
    diagram_data = DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                           versionId=temp_version_id,
                                           errorResponseFlag=False,
                                           objectName=new_diagram_name,
                                           diagramDescription=diagram_description)

    response_save = save_diagram(super_user, body=diagram_data)
    create_result: ResponseDto = response_save.body
    saved_version_id = create_result["uuid"]
    yield {"script_view": script_view, "create_result": create_result, "diagram_data": diagram_data,
           "template": template}

    # delete_diagram(super_user, saved_version_id)
    # delete_script_by_id(super_user, groovy_code_create_result.versionId)


@pytest.fixture()
def diagram_for_start(super_user, create_temp_diagram_gen):
    diagram_template = dict(create_temp_diagram_gen.create_template())
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template["inOutParameters"][0])
    param_name_inp = "input_var"
    parameter_version_id_inp = str(uuid.uuid4())
    param_name_out = "output_var"
    parameter_version_id_out = str(uuid.uuid4())
    diagram_param_inp = variable_construct(array_flag=False,
                                           complex_flag=False,
                                           default_value=None,
                                           is_execute_status=None,
                                           order_num=0,
                                           param_name=param_name_inp,
                                           parameter_type="in",
                                           parameter_version_id=parameter_version_id_inp,
                                           parameter_id=parameter_version_id_inp,
                                           type_id=1
                                           )
    diagram_param_out = variable_construct(array_flag=False,
                                           complex_flag=False,
                                           default_value=None,
                                           is_execute_status=None,
                                           order_num=0,
                                           param_name=param_name_out,
                                           parameter_type="in_out",
                                           parameter_version_id=parameter_version_id_out,
                                           parameter_id=parameter_version_id_out,
                                           type_id=1
                                           )

    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [diagram_exec_var,
                                                 diagram_param_inp, diagram_param_out])

    update_response: ResponseDto = params_response.body

    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id)
    node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id)
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    link_s_f = link_construct(temp_version_id, node_start.uuid, node_end.uuid)
    link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
    return {"template": diagram_template,
            "node_start_id": node_start.uuid,
            "diagram_param_inp": diagram_param_inp,
            "diagram_param_out": diagram_param_out}


@pytest.fixture()
def diagram_for_finish(super_user, create_temp_diagram_gen):
    diagram_template = dict(create_temp_diagram_gen.create_template())
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template["inOutParameters"][0])
    param_name_inp = "input_var"
    parameter_version_id_inp = str(uuid.uuid4())
    param_name_out = "output_var"
    parameter_version_id_out = str(uuid.uuid4())
    diagram_param_inp = variable_construct(array_flag=False,
                                           complex_flag=False,
                                           default_value=None,
                                           is_execute_status=None,
                                           order_num=0,
                                           param_name=param_name_inp,
                                           parameter_type="in",
                                           parameter_version_id=parameter_version_id_inp,
                                           parameter_id=parameter_version_id_inp,
                                           type_id=1
                                           )
    diagram_param_out = variable_construct(array_flag=False,
                                           complex_flag=False,
                                           default_value=None,
                                           is_execute_status=None,
                                           order_num=0,
                                           param_name=param_name_out,
                                           parameter_type="out",
                                           parameter_version_id=parameter_version_id_out,
                                           parameter_id=parameter_version_id_out,
                                           type_id=1
                                           )

    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [diagram_exec_var,
                                                 diagram_param_inp, diagram_param_out])

    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node("start", False, False, param_name_inp, 1,
                                         parameter_version_id_inp)

    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id)
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    link_s_f = link_construct(temp_version_id, node_start.uuid, node_end.uuid)
    link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
    return {"template": diagram_template,
            "node_finish_id": node_end.uuid,
            "diagram_param_inp": diagram_param_inp,
            "diagram_param_out": diagram_param_out}


@pytest.fixture()
def diagram_for_finish_two_var(super_user, create_temp_diagram_gen):
    diagram_template = dict(create_temp_diagram_gen.create_template())
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template["inOutParameters"][0])
    param_name_inp = "input_var"
    parameter_version_id_inp = str(uuid.uuid4())
    param_name_out = "output_var"
    param_name_out2 = "output_var2"
    parameter_version_id_out = str(uuid.uuid4())
    parameter_version_id_out2 = str(uuid.uuid4())
    diagram_param_inp = variable_construct(array_flag=False,
                                           complex_flag=False,
                                           default_value=None,
                                           is_execute_status=None,
                                           order_num=0,
                                           param_name=param_name_inp,
                                           parameter_type="in",
                                           parameter_version_id=parameter_version_id_inp,
                                           parameter_id=parameter_version_id_inp,
                                           type_id=1
                                           )
    diagram_param_out = variable_construct(array_flag=False,
                                           complex_flag=False,
                                           default_value=None,
                                           is_execute_status=None,
                                           order_num=0,
                                           param_name=param_name_out,
                                           parameter_type="out",
                                           parameter_version_id=parameter_version_id_out,
                                           parameter_id=parameter_version_id_out,
                                           type_id=1
                                           )
    diagram_param_out2 = variable_construct(array_flag=False,
                                            complex_flag=False,
                                            default_value=None,
                                            is_execute_status=None,
                                            order_num=0,
                                            param_name=param_name_out2,
                                            parameter_type="out",
                                            parameter_version_id=parameter_version_id_out2,
                                            parameter_id=parameter_version_id_out2,
                                            type_id=1
                                            )

    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [diagram_exec_var,
                                                 diagram_param_inp, diagram_param_out, diagram_param_out2])

    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node("start", False, False, param_name_inp, 1,
                                         parameter_version_id_inp)

    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id)
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    link_s_f = link_construct(temp_version_id, node_start.uuid, node_end.uuid)
    link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
    return {"template": diagram_template,
            "node_finish_id": node_end.uuid,
            "diagram_param_inp": diagram_param_inp,
            "diagram_param_out": diagram_param_out,
            "diagram_param_out2": diagram_param_out2}


@pytest.fixture()
def diagram_scorecard(super_user,
                      create_temp_diagram_gen):
    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    in_out_param_name = "in_out_v"
    in_out_parameter_version_id = str(uuid.uuid4())
    in_out_param = variable_construct(array_flag=False,
                                      complex_flag=False,
                                      default_value=None,
                                      is_execute_status=None,
                                      order_num=0,
                                      param_name=in_out_param_name,
                                      parameter_type="in_out",
                                      parameter_version_id=in_out_parameter_version_id,
                                      type_id=1,
                                      parameter_id=in_out_parameter_version_id)
    score_param_name = "score_v"
    score_parameter_version_id = str(uuid.uuid4())
    score_param = variable_construct(array_flag=False,
                                     complex_flag=False,
                                     default_value=None,
                                     is_execute_status=None,
                                     order_num=0,
                                     param_name=score_param_name,
                                     parameter_type="in",
                                     parameter_version_id=score_parameter_version_id,
                                     type_id=1,
                                     parameter_id=score_parameter_version_id)
    params_response = update_diagram_parameters(super_user, temp_version_id,
                                                [diagram_exec_var,
                                                 in_out_param, score_param])
    update_response: ResponseDto = params_response.body

    start_variable = variables_for_node(node_type="start", is_arr=False, is_compl=False,
                                        name=in_out_param_name, type_id=1,
                                        vers_id=in_out_parameter_version_id)
    start_variable2 = variables_for_node(node_type="start", is_arr=False, is_compl=False,
                                         name=score_param_name, type_id=1,
                                         vers_id=score_parameter_version_id)

    node_score = scorecard_node_construct(
        x=700, y=202.22915649414062, temp_version_id=temp_version_id
    )
    node_score_response: ResponseDto = ResponseDto.construct(
        **create_node(super_user, node_score).body
    )
    node_score_id = node_score_response.uuid
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id,
                                    [start_variable, start_variable2])
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id)
    node_start: ResponseDto = ResponseDto.construct(
        **create_node(super_user, node_start_raw).body)
    node_start_id = node_start.uuid
    node_end: ResponseDto = ResponseDto.construct(
        **create_node(super_user, node_finish_raw).body)
    node_end_id = node_end.uuid

    link_s_sc = link_construct(
        temp_version_id, node_start_id, node_score_id
    )
    link_s_sc_create_response: ResponseDto = ResponseDto.construct(
        **create_link(super_user, body=link_s_sc).body
    )
    link_s_sc_id = link_s_sc_create_response.uuid
    link_sc_f = link_construct(
        temp_version_id, node_score_id, node_end_id
    )
    link_sc_f_create_response: ResponseDto = ResponseDto.construct(
        **create_link(super_user, body=link_sc_f).body
    )
    link_sc_f_id = link_sc_f_create_response.uuid

    finish_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False,
                                         name=1,
                                         param_name=in_out_param_name,
                                         type_id="1",
                                         vers_id=in_out_parameter_version_id)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.uuid, body=finish_up_body
    )
    return {"node_score_id": node_score_id, "temp_version_id": temp_version_id,
            "score_param": score_param}


@pytest.fixture()
def diagram_all_prim_v_one_node_indirect(super_user,
                                         create_temp_diagram_gen,
                                         request):
    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])

    in_param_name = "in_v"
    in_int_param_name = "in_int_v"
    in_float_param_name = "in_float_v"
    in_str_param_name = "in_str_v"
    in_bool_param_name = "in_bool_v"
    in_date_param_name = "in_date_v"
    in_date_time_param_name = "in_date_time_v"
    in_time_param_name = "in_time_v"
    in_long_param_name = "in_long_v"

    out_int_param_name = "out_int_v"
    out_float_param_name = "out_float_v"
    out_long_param_name = "out_long_v"
    out_str_param_name = "out_str_v"
    out_bool_param_name = "out_bool_v"
    out_date_param_name = "out_date_v"
    out_date_time_param_name = "out_date_time_v"
    out_time_param_name = "out_time_v"

    in_int_parameter_version_id = str(uuid.uuid4())
    in_float_parameter_version_id = str(uuid.uuid4())
    in_str_parameter_version_id = str(uuid.uuid4())
    in_date_parameter_version_id = str(uuid.uuid4())
    in_bool_parameter_version_id = str(uuid.uuid4())
    in_date_time_parameter_version_id = str(uuid.uuid4())
    in_time_parameter_version_id = str(uuid.uuid4())
    in_long_parameter_version_id = str(uuid.uuid4())
    in_parameter_version_id = str(uuid.uuid4())

    out_int_parameter_version_id = str(uuid.uuid4())
    out_float_parameter_version_id = str(uuid.uuid4())
    out_long_parameter_version_id = str(uuid.uuid4())
    out_str_parameter_version_id = str(uuid.uuid4())
    out_date_parameter_version_id = str(uuid.uuid4())
    out_bool_parameter_version_id = str(uuid.uuid4())
    out_date_time_parameter_version_id = str(uuid.uuid4())
    out_time_parameter_version_id = str(uuid.uuid4())

    in_param = variable_construct(array_flag=request.param["array_flag"],
                                  complex_flag=False,
                                  default_value=None,
                                  is_execute_status=None,
                                  order_num=1,
                                  param_name=in_param_name,
                                  parameter_type="in",
                                  parameter_version_id=in_parameter_version_id,
                                  type_id=2,
                                  parameter_id=in_parameter_version_id)
    in_int_param = variable_construct(array_flag=request.param["array_flag"],
                                      complex_flag=False,
                                      default_value=None,
                                      is_execute_status=None,
                                      order_num=2,
                                      param_name=in_int_param_name,
                                      parameter_type="in",
                                      parameter_version_id=in_int_parameter_version_id,
                                      type_id=1,
                                      parameter_id=in_int_parameter_version_id)
    in_float_param = variable_construct(array_flag=request.param["array_flag"],
                                        complex_flag=False,
                                        default_value=None,
                                        is_execute_status=None,
                                        order_num=3,
                                        param_name=in_float_param_name,
                                        parameter_type="in",
                                        parameter_version_id=in_float_parameter_version_id,
                                        type_id=0,
                                        parameter_id=in_float_parameter_version_id)
    in_str_param = variable_construct(array_flag=request.param["array_flag"],
                                      complex_flag=False,
                                      default_value=None,
                                      is_execute_status=None,
                                      order_num=4,
                                      param_name=in_str_param_name,
                                      parameter_type="in",
                                      parameter_version_id=in_str_parameter_version_id,
                                      type_id=2,
                                      parameter_id=in_str_parameter_version_id)
    in_date_param = variable_construct(array_flag=request.param["array_flag"],
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=5,
                                       param_name=in_date_param_name,
                                       parameter_type="in",
                                       parameter_version_id=in_date_parameter_version_id,
                                       type_id=3,
                                       parameter_id=in_date_parameter_version_id)
    in_bool_param = variable_construct(array_flag=request.param["array_flag"],
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=6,
                                       param_name=in_bool_param_name,
                                       parameter_type="in",
                                       parameter_version_id=in_bool_parameter_version_id,
                                       type_id=4,
                                       parameter_id=in_bool_parameter_version_id)
    in_date_time_param = variable_construct(array_flag=request.param["array_flag"],
                                            complex_flag=False,
                                            default_value=None,
                                            is_execute_status=None,
                                            order_num=7,
                                            param_name=in_date_time_param_name,
                                            parameter_type="in",
                                            parameter_version_id=in_date_time_parameter_version_id,
                                            type_id=5,
                                            parameter_id=in_date_time_parameter_version_id)
    in_time_param = variable_construct(array_flag=request.param["array_flag"],
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=8,
                                       param_name=in_time_param_name,
                                       parameter_type="in",
                                       parameter_version_id=in_time_parameter_version_id,
                                       type_id=6,
                                       parameter_id=in_time_parameter_version_id)
    in_long_param = variable_construct(array_flag=request.param["array_flag"],
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=9,
                                       param_name=in_long_param_name,
                                       parameter_type="in",
                                       parameter_version_id=in_long_parameter_version_id,
                                       type_id=7,
                                       parameter_id=in_long_parameter_version_id)

    out_int_param = variable_construct(array_flag=False,
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=0,
                                       param_name=out_int_param_name,
                                       parameter_type="out",
                                       parameter_version_id=out_int_parameter_version_id,
                                       type_id=1,
                                       parameter_id=out_int_parameter_version_id)
    out_float_param = variable_construct(array_flag=False,
                                         complex_flag=False,
                                         default_value=None,
                                         is_execute_status=None,
                                         order_num=0,
                                         param_name=out_float_param_name,
                                         parameter_type="out",
                                         parameter_version_id=out_float_parameter_version_id,
                                         type_id=0,
                                         parameter_id=out_float_parameter_version_id)
    out_long_param = variable_construct(array_flag=False,
                                        complex_flag=False,
                                        default_value=None,
                                        is_execute_status=None,
                                        order_num=0,
                                        param_name=out_long_param_name,
                                        parameter_type="out",
                                        parameter_version_id=out_long_parameter_version_id,
                                        type_id=7,
                                        parameter_id=out_long_parameter_version_id)
    out_str_param = variable_construct(array_flag=False,
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=0,
                                       param_name=out_str_param_name,
                                       parameter_type="out",
                                       parameter_version_id=out_str_parameter_version_id,
                                       type_id=2,
                                       parameter_id=out_str_parameter_version_id)
    out_date_param = variable_construct(array_flag=False,
                                        complex_flag=False,
                                        default_value=None,
                                        is_execute_status=None,
                                        order_num=0,
                                        param_name=out_date_param_name,
                                        parameter_type="out",
                                        parameter_version_id=out_date_parameter_version_id,
                                        type_id=3,
                                        parameter_id=out_date_parameter_version_id)
    out_bool_param = variable_construct(array_flag=False,
                                        complex_flag=False,
                                        default_value=None,
                                        is_execute_status=None,
                                        order_num=0,
                                        param_name=out_bool_param_name,
                                        parameter_type="out",
                                        parameter_version_id=out_bool_parameter_version_id,
                                        type_id=4,
                                        parameter_id=out_bool_parameter_version_id)
    out_date_time_param = variable_construct(array_flag=False,
                                             complex_flag=False,
                                             default_value=None,
                                             is_execute_status=None,
                                             order_num=0,
                                             param_name=out_date_time_param_name,
                                             parameter_type="out",
                                             parameter_version_id=out_date_time_parameter_version_id,
                                             type_id=5,
                                             parameter_id=out_date_time_parameter_version_id)
    out_time_param = variable_construct(array_flag=False,
                                        complex_flag=False,
                                        default_value=None,
                                        is_execute_status=None,
                                        order_num=0,
                                        param_name=out_time_param_name,
                                        parameter_type="out",
                                        parameter_version_id=out_time_parameter_version_id,
                                        type_id=6,
                                        parameter_id=out_time_parameter_version_id)

    params_response = update_diagram_parameters(super_user, temp_version_id,
                                                [diagram_exec_var,
                                                 in_param,
                                                 in_int_param,
                                                 in_float_param,
                                                 in_str_param,
                                                 in_date_param,
                                                 in_bool_param,
                                                 in_date_time_param,
                                                 in_time_param,
                                                 in_long_param,
                                                 out_int_param,
                                                 out_float_param,
                                                 out_long_param,
                                                 out_str_param,
                                                 out_date_param,
                                                 out_bool_param,
                                                 out_date_time_param,
                                                 out_time_param,
                                                 ])
    update_response: ResponseDto = params_response.body

    start_int_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                            name=in_int_param.parameterName,
                                            type_id=in_int_param.typeId,
                                            vers_id=in_int_param.parameterVersionId)
    start_float_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                              name=in_float_param.parameterName,
                                              type_id=in_float_param.typeId,
                                              vers_id=in_float_param.parameterVersionId)
    start_str_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                            name=in_str_param.parameterName,
                                            type_id=in_str_param.typeId,
                                            vers_id=in_str_param.parameterVersionId)
    start_date_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                             name=in_date_param.parameterName,
                                             type_id=in_date_param.typeId,
                                             vers_id=in_date_param.parameterVersionId)
    start_bool_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                             name=in_bool_param.parameterName,
                                             type_id=in_bool_param.typeId,
                                             vers_id=in_bool_param.parameterVersionId)
    start_date_time_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                                  name=in_date_time_param.parameterName,
                                                  type_id=in_date_time_param.typeId,
                                                  vers_id=in_date_time_param.parameterVersionId)
    start_time_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                             name=in_time_param.parameterName,
                                             type_id=in_time_param.typeId,
                                             vers_id=in_time_param.parameterVersionId)
    start_long_variable = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                             name=in_long_param.parameterName,
                                             type_id=in_long_param.typeId,
                                             vers_id=in_long_param.parameterVersionId)
    start_variable2 = variables_for_node(node_type="start", is_arr=request.param["array_flag"], is_compl=False,
                                         name=in_param.parameterName, type_id=in_param.typeId,
                                         vers_id=in_param.parameterVersionId)
    testing_node_id = None
    if request.param["node"] == "scorecard":
        testing_node = scorecard_node_construct(
            x=700, y=202.22915649414062, temp_version_id=temp_version_id
        )
        testing_node_response: ResponseDto = ResponseDto.construct(
            **create_node(super_user, testing_node).body
        )
        testing_node_id = testing_node_response.uuid
    if request.param["node"] == "var_calc":
        testing_node = node_construct(
            700, 202.22915649414062, "var_calc", temp_version_id=temp_version_id
        )
        testing_node_response: ResponseDto = ResponseDto.construct(
            **create_node(super_user, testing_node).body
        )
        testing_node_id = testing_node_response.uuid
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id,
                                    [start_int_variable,
                                     start_float_variable,
                                     start_str_variable,
                                     start_date_variable,
                                     start_bool_variable,
                                     start_date_time_variable,
                                     start_time_variable,
                                     start_long_variable,
                                     start_variable2])
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id)
    node_start: ResponseDto = ResponseDto.construct(
        **create_node(super_user, node_start_raw).body)
    node_start_id = node_start.uuid
    node_end: ResponseDto = ResponseDto.construct(
        **create_node(super_user, node_finish_raw).body)
    node_end_id = node_end.uuid

    link_s_sc = link_construct(
        temp_version_id, node_start_id, testing_node_id
    )
    link_s_sc_create_response: ResponseDto = ResponseDto.construct(
        **create_link(super_user, body=link_s_sc).body
    )
    link_s_sc_id = link_s_sc_create_response.uuid
    link_sc_f = link_construct(
        temp_version_id, testing_node_id, node_end_id
    )
    link_sc_f_create_response: ResponseDto = ResponseDto.construct(
        **create_link(super_user, body=link_sc_f).body
    )
    link_sc_f_id = link_sc_f_create_response.uuid

    finish_int_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                             name=1,
                                             param_name=out_int_param.parameterName,
                                             type_id=out_int_param.typeId,
                                             vers_id=out_int_param.parameterVersionId)
    finish_float_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                               name=1.0,
                                               param_name=out_float_param.parameterName,
                                               type_id=out_float_param.typeId,
                                               vers_id=out_float_param.parameterVersionId)
    finish_long_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                              name=1,
                                              param_name=out_long_param.parameterName,
                                              type_id=out_long_param.typeId,
                                              vers_id=out_long_param.parameterVersionId)
    finish_str_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                             name="'some_string'",
                                             param_name=out_str_param.parameterName,
                                             type_id=out_str_param.typeId,
                                             vers_id=out_str_param.parameterVersionId)
    finish_date_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                              name="'2023-04-23'",
                                              param_name=out_date_param.parameterName,
                                              type_id=out_date_param.typeId,
                                              vers_id=out_date_param.parameterVersionId)
    finish_bool_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                              name="'true'",
                                              param_name=out_bool_param.parameterName,
                                              type_id=out_bool_param.typeId,
                                              vers_id=out_bool_param.parameterVersionId)
    finish_date_time_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                                   name="'2023-04-24 17:06:13'",
                                                   param_name=out_date_time_param.parameterName,
                                                   type_id=out_date_time_param.typeId,
                                                   vers_id=out_date_time_param.parameterVersionId)
    finish_time_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False, is_literal=True,
                                              name="'09:00:00'",
                                              param_name=out_time_param.parameterName,
                                              type_id=out_time_param.typeId,
                                              vers_id=out_time_param.parameterVersionId)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_int_variable,
                                                      finish_float_variable,
                                                      finish_long_variable,
                                                      finish_str_variable,
                                                      finish_date_variable,
                                                      finish_bool_variable,
                                                      finish_date_time_variable,
                                                      finish_time_variable])
    update_node(
        super_user, node_id=node_end.uuid, body=finish_up_body
    )
    all_in_params = [in_param,
                     in_int_param,
                     in_float_param,
                     in_str_param,
                     in_date_param,
                     in_bool_param,
                     in_date_time_param,
                     in_time_param,
                     in_long_param]
    all_out_params = [out_int_param,
                      out_float_param,
                      out_long_param,
                      out_str_param,
                      out_date_param,
                      out_bool_param,
                      out_date_time_param,
                      out_time_param]
    array_flag = request.param["array_flag"]
    return {"testing_node_id": testing_node_id, "node_end_id": node_end_id,
            "node_start_id": node_start_id,
            "temp_version_id": temp_version_id,
            "array_flag": array_flag,
            "diagram_id": diagram_id,
            "in_int_param": in_int_param,
            "in_float_param": in_float_param,
            "in_str_param": in_str_param,
            "in_date_param": in_date_param,
            "in_bool_param": in_bool_param,
            "in_date_time_param": in_date_time_param,
            "in_time_param": in_time_param,
            "in_long_param": in_long_param,
            "all_in_params": all_in_params,
            "all_out_params": all_out_params,
            "diagram_exec_var": diagram_exec_var}
