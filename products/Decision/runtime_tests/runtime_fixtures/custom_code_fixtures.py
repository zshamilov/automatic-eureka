import uuid

import pytest

from common.generators import generate_string
from products.Decision.framework.model import VariableType1, ScriptFullView, ScriptVariableFullView, NodeViewShortInfo, \
    DiagramInOutParameterFullViewDto, ScriptType2, NodeValidateDto, NodeViewWithVariablesDto, DiagramCreateNewVersion, \
    DiagramViewDto, PythonEnvironmentSettingsWithoutIdDto, PythonEnvironmentCreateDto
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version, delete_diagram, \
    put_diagram_submit
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.framework.steps.decision_steps_python_environment import create_python_environment, \
    get_environment_versions_by_version_id, delete_python_environment, get_environment_python_version
from products.Decision.framework.steps.decision_steps_python_version import get_python_version_list
from products.Decision.framework.steps.decision_steps_script_api import create_python_script, get_python_script_by_id, \
    delete_script_by_id, create_groovy_script, get_groovy_script_by_id
from products.Decision.utilities.custom_code_constructors import script_vars_construct, code_construct, \
    script_environment_construct, python_environment_setting_construct
from products.Decision.utilities.node_cunstructors import variables_for_node, node_update_construct


@pytest.fixture()
def diagram_custom_code_python_2(super_user, diagram_constructor, save_diagrams_gen):
    inp_var = script_vars_construct(var_name="input_int",
                                    var_type=VariableType1.IN,
                                    is_array=False, primitive_id="1")
    out_var = script_vars_construct(var_name="output_int",
                                    var_type=VariableType1.OUT,
                                    is_array=False, primitive_id="1")
    script_text = "def run(data: dict):\n  return {'output_int': data['input_int'] * 5}"
    script_name = "ag_python_script_" + generate_string()
    script = code_construct(script_type="python",
                            script_name=script_name,
                            script_text=script_text,
                            variables=[inp_var, out_var])
    python_code_create_result = ScriptFullView.construct(
        **create_python_script(super_user, body=script).body)
    script_view = ScriptFullView.construct(
        **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
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
    script_id = script_view.scriptId
    script_version_id = script_view.versionId
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_custom_code: NodeViewShortInfo = diagram_constructor["nodes"]["кастомный код"]
    diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
    node_custom_code_id = node_custom_code.nodeId
    out_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=output_var_with_id.variableName,
                                     type_id=output_var_with_id.primitiveTypeId,
                                     outer_variable_id=output_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    inp_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=input_var_with_id.variableName,
                                     type_id=input_var_with_id.primitiveTypeId,
                                     outer_variable_id=input_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                            temp_version_id=temp_version_id,
                                            script_id=script_id, script_version_id=script_version_id,
                                            script_type=ScriptType2.PYTHON,
                                            inp_custom_code_vars=[inp_var_map], out_custom_code_vars=[out_var_map])
    update_node(super_user, node_id=node_custom_code.nodeId, body=node_script_upd,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=node_script_upd.nodeTypeId,
                    properties=node_script_upd.properties))
    script_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_custom_code.nodeId).body)
    finish_variable = variables_for_node("finish", False, False, diagram_param.parameterName, 1,
                                         diagram_param.parameterId)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.nodeId, body=finish_up_body
    )
    new_diagram_name = "ag_diagram_script" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    yield {"script_view": script_view, "create_result": create_result, "diagram_param": diagram_param,
           "diagram_name": new_diagram_name, "saved_version_id": saved_version_id,
           "diagram_id": diagram_id, "temp_script_node_id": node_custom_code_id, "temp_version_id": temp_version_id}

    try:
        delete_diagram(super_user, saved_version_id)
    except:
        print("запрос на удаление диаграммы не исполнен")
    try:
        delete_script_by_id(super_user, python_code_create_result.versionId)
    except:
        print("запрос на удаление скрипта не исполнен")


@pytest.fixture()
def diagram_python_environment(super_user, get_env):
    environment_id = get_env.get_env_id()
    environment = python_environment_setting_construct(
        limits_cpu=0.3,
        requests_cpu=0.1,
        limits_memory=128,
        requests_memory=64,
        environment_id=environment_id)
    environment_name = "test_python_environment_" + generate_string()
    python_versions = get_python_version_list(super_user)
    python_version_id = python_versions[0].id
    requirements_txt = "pandas"
    body = script_environment_construct(name=environment_name,
                                        python_version_id=python_version_id,
                                        requirements_txt=requirements_txt,
                                        python_environment_setting=[environment])
    python_environment = create_python_environment(super_user, body)
    vers_id = python_environment.body["uuid"]
    resp = get_environment_python_version(super_user, vers_id)
    ver_id = resp.body["versionId"]
    yield {"python_environment_info": resp,
           "python_version_id": python_version_id,
           "python_environment_id": environment_id,
           "python_environment_version_id": ver_id}

    # delete_python_environment(super_user, vers_id)


@pytest.fixture()
def diagram_custom_code_python_environment(super_user,
                                           diagram_python_environment, diagram_constructor, save_diagrams_gen):
    python_environment_version = diagram_python_environment["python_environment_version_id"]
    inp_var = script_vars_construct(var_name="input_int",
                                    var_type=VariableType1.IN,
                                    is_array=False, primitive_id="1")
    out_var = script_vars_construct(var_name="output_int",
                                    var_type=VariableType1.OUT,
                                    is_array=False, primitive_id="1")

    script_text = "import pandas\ndef run(data: dict):\n  return {'output_int': data['input_int'] * 5}"
    script_name = "ag_python_script_" + generate_string()
    script = code_construct(script_type="python",
                            script_name=script_name,
                            script_text=script_text,
                            python_environment_version_id=python_environment_version,
                            variables=[inp_var, out_var])
    python_code_create_result = ScriptFullView.construct(
        **create_python_script(super_user, body=script).body)
    script_view = ScriptFullView.construct(
        **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
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
    script_id = script_view.scriptId
    script_version_id = script_view.versionId
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_custom_code: NodeViewShortInfo = diagram_constructor["nodes"]["кастомный код"]
    diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
    node_custom_code_id = node_custom_code.nodeId
    out_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=output_var_with_id.variableName,
                                     type_id=output_var_with_id.primitiveTypeId,
                                     outer_variable_id=output_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    inp_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=input_var_with_id.variableName,
                                     type_id=input_var_with_id.primitiveTypeId,
                                     outer_variable_id=input_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                            temp_version_id=temp_version_id,
                                            script_id=script_id, script_version_id=script_version_id,
                                            script_type=ScriptType2.PYTHON,
                                            inp_custom_code_vars=[inp_var_map], out_custom_code_vars=[out_var_map])
    update_node(super_user, node_id=node_custom_code.nodeId, body=node_script_upd,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=node_script_upd.nodeTypeId,
                    properties=node_script_upd.properties))
    script_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_custom_code.nodeId).body)
    finish_variable = variables_for_node("finish", False, False, diagram_param.parameterName, 1,
                                         diagram_param.parameterId)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.nodeId, body=finish_up_body
    )
    new_diagram_name = "ag_diagram_script" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    yield {"script_view": script_view, "create_result": create_result, "diagram_param": diagram_param,
           "diagram_name": new_diagram_name, "saved_version_id": saved_version_id,
           "diagram_id": diagram_id, "temp_script_node_id": node_custom_code_id, "temp_version_id": temp_version_id}

    try:
        delete_diagram(super_user, saved_version_id)
    except:
        print("запрос на удаление диаграммы не исполнен")
    try:
        delete_script_by_id(super_user, python_code_create_result.versionId)
    except:
        print("запрос на удаление скрипта не исполнен")


@pytest.fixture()
def diagram_python_script_submit_2(super_user, get_env, diagram_custom_code_python_2):
    diagram_id = diagram_custom_code_python_2["diagram_id"]
    diagram_name = diagram_custom_code_python_2["diagram_name"]
    diagram_param = diagram_custom_code_python_2["diagram_param"]
    put_diagram_submit(super_user, diagram_id)
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    env_id = get_env.get_env_id("default_dev")
    return {"deploy_id": deploy_id, "diagram_param": diagram_param,
            "env_id": env_id, "diagram_id": diagram_id,
            "diagram_name": diagram_name}


@pytest.fixture()
def diagram_custom_code_groovy_2(super_user, diagram_constructor, save_diagrams_gen):
    inp_var = script_vars_construct(var_name="input_int",
                                    var_type=VariableType1.IN,
                                    is_array=False, primitive_id="1")
    out_var = script_vars_construct(var_name="output_int",
                                    var_type=VariableType1.OUT,
                                    is_array=False, primitive_id="1")
    script_text = "output_int = input_int + 5"
    script_name = "ag_groovy_script_" + generate_string()
    script = code_construct(script_type="groovy",
                            script_name=script_name,
                            script_text=script_text,
                            variables=[inp_var, out_var])
    groovy_code_create_result = ScriptFullView.construct(
        **create_groovy_script(super_user, body=script).body)
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
    script_id = script_view.scriptId
    script_version_id = script_view.versionId
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_custom_code: NodeViewShortInfo = diagram_constructor["nodes"]["кастомный код"]
    diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
    node_custom_code_id = node_custom_code.nodeId
    out_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=out_var.variableName,
                                     type_id=out_var.primitiveTypeId,
                                     outer_variable_id=output_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    inp_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=inp_var.variableName,
                                     type_id=inp_var.primitiveTypeId,
                                     outer_variable_id=input_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                            temp_version_id=temp_version_id,
                                            script_id=script_id, script_version_id=script_version_id,
                                            script_type=ScriptType2.GROOVY,
                                            inp_custom_code_vars=[inp_var_map], out_custom_code_vars=[out_var_map])
    update_node(super_user, node_id=node_custom_code_id, body=node_script_upd,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=node_script_upd.nodeTypeId,
                    properties=node_script_upd.properties))
    finish_variable = variables_for_node("finish", False, False, diagram_param.parameterName, 1,
                                         diagram_param.parameterId)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.nodeId, body=finish_up_body
    )
    new_diagram_name = "ag_diagram_script" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    yield {"script_view": script_view, "create_result": create_result, "diagram_param": diagram_param,
           "diagram_name": new_diagram_name, "saved_version_id": saved_version_id,
           "diagram_id": diagram_id, "temp_script_node_id": node_custom_code_id}


@pytest.fixture()
def diagram_groovy_script_submit_2(super_user, get_env, diagram_custom_code_groovy_2):
    diagram_id = diagram_custom_code_groovy_2["diagram_id"]
    diagram_name = diagram_custom_code_groovy_2["diagram_name"]
    diagram_param = diagram_custom_code_groovy_2["diagram_param"]
    put_diagram_submit(super_user, diagram_id)
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    env_id = get_env.get_env_id("default_dev")
    return {"deploy_id": deploy_id, "diagram_param": diagram_param,
            "env_id": env_id, "diagram_id": diagram_id,
            "diagram_name": diagram_name}


@pytest.fixture()
def diagram_custom_code_groovy_2_nodes(super_user, diagram_constructor, save_diagrams_gen):
    inp_var = script_vars_construct(var_name="input_int",
                                    var_type=VariableType1.IN,
                                    is_array=False, primitive_id="1")
    out_var = script_vars_construct(var_name="output_int",
                                    var_type=VariableType1.OUT,
                                    is_array=False, primitive_id="1")
    script_text = "output_int = input_int + 5"
    script_name = "ag_groovy_script_" + generate_string()
    script = code_construct(script_type="groovy",
                            script_name=script_name,
                            script_text=script_text,
                            variables=[inp_var, out_var])
    groovy_code_create_result = ScriptFullView.construct(
        **create_groovy_script(super_user, body=script).body)
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

    script_id = script_view.scriptId
    script_version_id = script_view.versionId
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
    diagram_id = diagram_constructor["diagram_info"].diagramId
    node_script1: NodeViewShortInfo = diagram_constructor["nodes"]["кастомный код 1"]
    node_script_id1 = node_script1.nodeId
    node_script2: NodeViewShortInfo = diagram_constructor["nodes"]["кастомный код 2"]
    node_script_id2 = node_script2.nodeId

    out_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=out_var.variableName,
                                     type_id=out_var.primitiveTypeId,
                                     outer_variable_id=output_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    inp_var_map = variables_for_node(node_type="custom_code",
                                     is_arr=False, is_compl=False,
                                     name=diagram_param.parameterName,
                                     node_variable=inp_var.variableName,
                                     type_id=inp_var.primitiveTypeId,
                                     outer_variable_id=input_var_with_id.variableId,
                                     param_id=diagram_param.parameterId)
    node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                            temp_version_id=temp_version_id,
                                            script_id=script_id, script_version_id=script_version_id,
                                            script_type=ScriptType2.GROOVY,
                                            inp_custom_code_vars=[inp_var_map], out_custom_code_vars=[out_var_map])

    update_node(super_user, node_id=node_script_id1, body=node_script_upd,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=node_script_upd.nodeTypeId,
                    properties=node_script_upd.properties))

    update_node(super_user, node_id=node_script_id2, body=node_script_upd,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=node_script_upd.nodeTypeId,
                    properties=node_script_upd.properties))

    new_diagram_name = "ag_diagram_script" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    yield {"script_view": script_view, "create_result": create_result, "diagram_param": diagram_param,
           "diagram_name": new_diagram_name, "saved_version_id": saved_version_id,
           "diagram_id": diagram_id, "temp_script_node_id1": node_script_id1,
           "temp_script_node_id2": node_script_id2}
