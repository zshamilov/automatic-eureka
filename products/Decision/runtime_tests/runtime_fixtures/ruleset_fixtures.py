import pytest

from common.generators import generate_string
from products.Decision.framework.model import RuleTypeGetFullView, DiagramInOutParameterFullViewDto, NodeViewShortInfo, \
    DiagramViewDto, NodeViewWithVariablesDto, ComplexTypeGetFullView
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.framework.steps.decision_steps_rule_types_api import ruletype_list
from products.Decision.utilities.node_cunstructors import rule_set_var_const, rule_set_properties, \
    ruleset_node_construct, variables_for_node, node_update_construct


@pytest.fixture()
def diagram_ruleset_saved(super_user, diagram_constructor, save_diagrams_gen, request):
    rule_id = None
    rules = []
    for rule in ruletype_list(super_user).body.values():
        rules.append(RuleTypeGetFullView.construct(**rule))
    for rule in rules:
        if rule.typeName == "Decline":
            rule_id = rule.typeId

    expression_var_marker = request.node.get_closest_marker("expression_var")
    if expression_var_marker is not None:
        expression_type = expression_var_marker.args[0]
    else:
        expression_type = "constant"

    temp_version_id = diagram_constructor["diagram_info"].versionId
    diagram_id = diagram_constructor["diagram_info"].diagramId
    in_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
    out_rules_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_rule_result"]
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    node_rule: NodeViewShortInfo = diagram_constructor["nodes"]["набор правил"]

    rule_var_name = "rule_var"
    rule_var = rule_set_var_const(
        is_arr=True,
        is_complex=True,
        var_name=rule_var_name,
        type_id=out_rules_param.typeId,
        var_path=None,
        var_root_id=None,
    )
    if expression_type == 'constant':
        rule_properties = rule_set_properties(
            apply_rule=True,
            rule_name="test_rule",
            rule_code="test",
            rule_type_id=rule_id,
            rule_description="made in test",
            rule_expression="6 > 5",
            rule_weight_factor=1.0,
        )
    elif expression_type == 'primitive':
        rule_properties = rule_set_properties(
            apply_rule=True,
            rule_name="test_rule",
            rule_code="test",
            rule_type_id=rule_id,
            rule_description="made in test",
            rule_expression=f"${in_param.parameterName}>5",
            rule_weight_factor=1.0,
        )
    elif expression_type == 'complex':
        complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
            **get_custom_type(super_user, in_param.typeId).body
        )
        rule_properties = rule_set_properties(
            apply_rule=True,
            rule_name="test_rule",
            rule_code="test",
            rule_type_id=rule_id,
            rule_description="made in test",
            rule_expression=f"${in_param.parameterName}.{complex_type.attributes[0]['attributeName']} > 1",
            rule_weight_factor=1.0,
        )
    node_rule_upd = ruleset_node_construct(
        x=700,
        y=202.22915649414062,
        temp_version_id=temp_version_id,
        rule_variable=rule_var,
        rules=[rule_properties],
        operation="update",
    )
    update_node(
        super_user, node_id=node_rule.nodeId, body=node_rule_upd
    )
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_rule.nodeId).body)

    finish_variable = variables_for_node(node_type="finish_out", is_arr=True, is_compl=True,
                                         name=rule_var_name,
                                         param_name=out_rules_param.parameterName,
                                         type_id=out_rules_param.typeId,
                                         vers_id=out_rules_param.parameterVersionId,
                                         param_id=node_view.properties["ruleVariable"]["id"])
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.nodeId, body=finish_up_body
    )

    new_diagram_name = "diagram_ruleset" + "_" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)
    diagram_nodes = diagram_constructor["nodes"]

    return {"diagram_name": new_diagram_name, "diagram_data": save_data, "diagram_nodes": diagram_nodes,
            "in_diagram_param": in_param, "out_diagram_param": out_rules_param}