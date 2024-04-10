import pytest

from common.generators import generate_string
from products.Decision.framework.model import DiagramViewDto, DiagramInOutParameterFullViewDto, NodeViewShortInfo
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_diagram_helpers import upload_scorecard_file
from products.Decision.framework.steps.decision_steps_nodes import update_node
from products.Decision.utilities.node_cunstructors import scorecard_output_var, score_val_construct, \
    scorecard_input_var, scorecard_node_construct, variables_for_node, node_update_construct, scorecard_properties


@pytest.fixture()
def diagram_scorecard(super_user, diagram_constructor, save_diagrams_gen):
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    score_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["score_v"]
    in_out_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_v"]
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_score: NodeViewShortInfo = diagram_constructor["nodes"]["скоркарта"]
    score_var_name = "new_v"
    output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                            is_dict=False, default_value=1,
                                            name=score_var_name, type_id="1")
    score_val = score_val_construct(min_value=1,
                                    max_value=10,
                                    include_min_val=False,
                                    include_max_val=True,
                                    value=None,
                                    score_value=10)
    input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                          default_value=1, is_dict=False,
                                          name=score_param.parameterName, type_id=1,
                                          score_values=[score_val],
                                          param_id=score_param.parameterId)
    score_properties = scorecard_properties(output_variable=output_score_var,
                                            input_variables=[input_score_var])
    node_score_upd = scorecard_node_construct(
        x=700,
        y=202.22915649414062,
        temp_version_id=temp_version_id,
        properties=score_properties,
        operation="update",
    )
    update_node(
        super_user, node_id=node_score.nodeId, body=node_score_upd
    )

    finish_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False,
                                         name=score_var_name,
                                         param_name=in_out_param.parameterName,
                                         type_id=in_out_param.typeId,
                                         vers_id=in_out_param.parameterVersionId)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.nodeId, body=finish_up_body
    )

    new_diagram_name = "diagram_scorecard" + "_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def diagram_scorecard_from_excel(super_user, diagram_constructor, save_diagrams_gen):
    temp_version_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["a"]
    output_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["b"]
    scorecard_node: NodeViewShortInfo = diagram_constructor["nodes"]["скоркарта"]
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    score_values = upload_scorecard_file(super_user,
                                         "products/Decision/resources/scorecard_test_values.xlsx")[0].scoreValues
    input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                          default_value=1, is_dict=False,
                                          name=input_var.parameterName,
                                          type_id=input_var.typeId,
                                          score_values=score_values,
                                          param_id=input_var.parameterId)
    output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                            is_dict=False, default_value=2,
                                            name=output_var.parameterName,
                                            type_id=output_var.typeId,
                                            param_id=output_var.parameterId)
    score_properties = scorecard_properties(output_variable=output_score_var,
                                            input_variables=[input_score_var])
    node_score_upd = scorecard_node_construct(
        x=700,
        y=202.22915649414062,
        temp_version_id=temp_version_id,
        properties=score_properties,
        operation="update",
    )
    update_node(
        super_user, node_id=scorecard_node.nodeId, body=node_score_upd
    )

    finish_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False,
                                         name=output_var.parameterName,
                                         param_name=output_var.parameterName,
                                         type_id=output_var.typeId,
                                         vers_id=output_var.parameterVersionId)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.nodeId, body=finish_up_body
    )

    new_diagram_name = "diagram_scorecard" + "_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}
