import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, DiagramInOutParameterFullViewDto, NodeValidateDto, \
    DiagramViewDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node
from products.Decision.utilities.node_cunstructors import branch, default_branch, branch_node_properties, \
    branch_node_construct, variables_for_node, node_update_construct


@pytest.fixture()
def diagram_branch_saved(super_user, diagram_constructor, save_diagrams_gen, request):
    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
    link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
    node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
    node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]

    diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
    branch_type_marker = request.node.get_closest_marker("branch_type")
    if branch_type_marker is not None:
        branch_type = branch_type_marker.args[0]
    else:
        branch_type = "BRANCH_BY_ELEMENT"

    if branch_type == "BRANCH_BY_ELEMENT":
        branch_for_node = branch(link_id=link_b_f1_id,
                                 node_id=node_end1.nodeId,
                                 operator="GREATER",
                                 value_from="5")
        default_path = default_branch(node_id=node_end2.nodeId,
                                      link_id=link_b_f2_id)
        node_br_properties = branch_node_properties(branching_type="BRANCH_BY_ELEMENT",
                                                    condition=diagram_param.parameterName,
                                                    branching_value_type="1",
                                                    branches=[branch_for_node],
                                                    default_path=default_path)
    elif branch_type == "BRANCH_BY_CALCULATE_CONDITION":
        branch_for_node = branch(link_id=link_b_f1_id,
                                 node_id=node_end1.nodeId,
                                 operator="GREATER",
                                 value_from="5")
        default_path = default_branch(node_id=node_end2.nodeId,
                                      link_id=link_b_f2_id)
        node_br_properties = branch_node_properties(branching_type="BRANCH_BY_CALCULATE_CONDITION",
                                                    condition=f"${diagram_param.parameterName} + 1",
                                                    branching_value_type="1",
                                                    branches=[branch_for_node],
                                                    default_path=default_path)
    update_body = branch_node_construct(x=700, y=202.22915649414062,
                                        temp_version_id=temp_version_id,
                                        properties=node_br_properties,
                                        operation="update")
    update_node(super_user, node_id=node_branch.nodeId, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=node_br_properties))
    finish_variable1 = variables_for_node(node_type="finish_out",
                                          is_arr=False, is_compl=False,
                                          name="1", type_id=1,
                                          vers_id=diagram_param.parameterId,
                                          param_name=diagram_param.parameterName)
    finish_variable2 = variables_for_node(node_type="finish_out",
                                          is_arr=False, is_compl=False,
                                          name="2", type_id=1,
                                          vers_id=diagram_param.parameterId,
                                          param_name=diagram_param.parameterName)
    finish_up_body1 = node_update_construct(x=1800, y=202,
                                            temp_version_id=temp_version_id,
                                            node_type="finish",
                                            variables=[finish_variable1],
                                            node_name_up="Завершение")
    update_node(super_user, node_id=node_end1.nodeId, body=finish_up_body1)
    finish_up_body2 = node_update_construct(x=1800, y=402,
                                            temp_version_id=temp_version_id,
                                            node_type="finish",
                                            variables=[finish_variable2],
                                            node_name_up="Завершение_1")
    update_node(super_user, node_id=node_end2.nodeId, body=finish_up_body2)
    new_diagram_name = "diagram_branch" + "_" + generate_string()
    diagram_description = 'diagram created in test'

    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    diagram_nodes = diagram_constructor["nodes"]
    diagram_links = diagram_constructor["links"]
    print("diagram_links", diagram_links)
    yield {"diagram_name": new_diagram_name, "diagram_data": save_data, "diagram_param": diagram_param,
           "diagram_nodes": diagram_nodes, "diagram_links": diagram_links, "temp_version_id": temp_version_id}