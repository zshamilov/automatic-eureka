import uuid

import pytest

from common.generators import generate_string
from products.Decision.framework.model import DiagramInOutParameterFullViewDto, NodeViewShortInfo, UserJarFunctionsDto, \
    UserFunctionShortView, UserFunctionUploadView, UserFunctionShortInfo, DiagramViewDto, NodeValidateDto, \
    ComplexTypeGetFullView
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node
from products.Decision.utilities.node_cunstructors import node_update_construct, variables_for_node


@pytest.fixture()
def diagram_calc_func(super_user, diagram_constructor, upload_funcs_gen, save_diagrams_gen):
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    in_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
    out_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_var"]
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]

    upload_response: UserJarFunctionsDto = upload_funcs_gen.upload_jar_file(
        file="products/Decision/resources/user_funcs_testing.jar")
    jar_id = upload_response.jarId
    functions = upload_response.functions
    add_int_to_str: UserFunctionShortView = UserFunctionShortView.construct()
    for f in functions:
        if f.objectName == "returnString(java.lang.Integer)":
            add_int_to_str = f
    func_description = "made_in_test_" + generate_string()
    func_body = UserFunctionUploadView(objectName=add_int_to_str.objectName,
                                       jarFunctionName=add_int_to_str.jarFunctionName,
                                       functionClass=add_int_to_str.functionClass,
                                       resultType="2",
                                       description=func_description)
    user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func(jar_id, functions_body=[func_body])

    calc_val = f"${in_param.parameterName}"
    calc_var_name = 'inner_var'
    node_calc_vars = variables_for_node(
        node_type="var_calc",
        is_arr=False,
        is_compl=False,
        name=calc_var_name,
        type_id=2,
        calc_val=f"returnString({calc_val})",
        calc_type_id="2",
        func_ids=[user_func.id]
    )
    node_calc_upd = node_update_construct(
        700,
        202.22915649414062,
        "var_calc",
        temp_version_id,
        [node_calc_vars],
    )
    update_node(super_user, node_id=node_calc.nodeId, body=node_calc_upd)

    finish_variables = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False,
                                          name=calc_var_name, type_id=2, vers_id=out_param.parameterVersionId,
                                          param_name="out_var")
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.nodeId, body=finish_up_body)

    new_diagram_name = "diagram_calc_var" + "_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data,
            "create_result": create_result, "calc_val": calc_val,
            "in_param": in_param, "out_param": out_param,
            "temp_version_id": temp_version_id, "diagram_id": diagram_id}


@pytest.fixture()
def diagram_calc_prim_v(super_user, diagram_constructor, save_diagrams_gen, request):
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    in_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
    out_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_var"]
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]

    expression_var_marker = request.node.get_closest_marker("expression_var")
    if expression_var_marker is not None:
        expression_type = expression_var_marker.args[0]
    else:
        expression_type = "constant"

    if expression_type == 'constant':
        calc_val = 3
        node_calc_vars = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name=in_param.parameterName,
            type_id=in_param.typeId,
            calc_val=f"{calc_val}",
            calc_type_id="2",
            param_id=in_param.parameterId
        )
        finish_variables = variables_for_node(node_type="finish_out", is_arr=out_param.arrayFlag,
                                              is_compl=out_param.complexFlag,
                                              name=in_param.parameterName, type_id=out_param.typeId,
                                              vers_id=out_param.parameterVersionId,
                                              param_name=out_param.parameterName)
        finish_up_body = node_update_construct(x=1400, y=202,
                                               temp_version_id=temp_version_id,
                                               node_type="finish",
                                               variables=[finish_variables])
        update_node(super_user, node_id=node_end.nodeId, body=finish_up_body)

    elif expression_type == 'primitive':
        calc_val = f"${in_param.parameterName}",
        node_calc_vars = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name=out_param.parameterName,
            type_id=out_param.typeId,
            calc_val=f"${in_param.parameterName}",
            param_id=out_param.parameterId
        )
    elif expression_type == 'complex':
        complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
            **get_custom_type(super_user, in_param.typeId).body
        )
        calc_val = f"${in_param.parameterName}.{complex_type.attributes[0]['attributeName']}",
        node_calc_vars = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name=out_param.parameterName,
            type_id=out_param.typeId,
            calc_val=f"${in_param.parameterName}.{complex_type.attributes[0]['attributeName']}",
            param_id=out_param.parameterId
        )
    node_calc_upd = node_update_construct(
        700,
        202.22915649414062,
        "var_calc",
        diagram_constructor["temp_version_id"],
        [node_calc_vars],
    )

    update_node(super_user, node_id=node_calc.nodeId, body=node_calc_upd)

    new_diagram_name = "diagram_calc_var" + "_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    calc_node_id = None
    for node in save_data.nodes.values():
        if node["nodeName"] == "Расчет переменных":
            calc_node_id = node["nodeId"]

    return {"diagram_name": new_diagram_name, "diagram_data": save_data,
            "create_result": create_result, "calc_val": calc_val,
            "in_param": in_param, "out_param": out_param,
            "temp_version_id": temp_version_id, "diagram_id": diagram_id,
            "calc_node_id": calc_node_id}