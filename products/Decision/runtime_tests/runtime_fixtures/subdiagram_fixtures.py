import pytest

from common.generators import generate_string
from products.Decision.framework.model import DiagramInOutParameterFullViewDto, NodeViewWithVariablesDto, NodeRemapDto, \
    Properties, NodeUpdateDto
from products.Decision.framework.steps.decision_steps_nodes import get_node_by_id, remap_node, update_node, automap_node
from products.Decision.utilities.custom_models import IntNodeType


@pytest.fixture()
def diagram_with_subdiagram_in_subdiagram(super_user,
                                          diagram_subdiagram_working,
                                          diagram_constructor,
                                          save_diagrams_gen):
    subdiagram_version_id = diagram_subdiagram_working["outer_diagram_create_result"]["uuid"]
    subdiagram_id = diagram_subdiagram_working["outer_diagram_template"].diagramId
    temp_version_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_sub_id = diagram_constructor["nodes"]["поддиаграмма"].nodeId
    diagra_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["diagram_variable"]
    sub_node = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, node_sub_id).body)
    sub_node.properties = remap_node(super_user,
                                     node_sub_id,
                                     NodeRemapDto.construct(
                                         properties=Properties.construct(subdiagramId="",
                                                                         versionId="",
                                                                         inputVariablesMapping=[],
                                                                         outputVariablesMapping=[]),
                                         objectVersionId=subdiagram_version_id,
                                         objectId=subdiagram_id,
                                         nodeTypeId=IntNodeType.subdiagram.value)).body
    upd_body = NodeUpdateDto.construct(**sub_node.dict(), diagramVersionId=temp_version_id)
    update_node(super_user, node_id=node_sub_id, body=upd_body)
    sub_node = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, node_sub_id).body)
    automap_result_for_output = automap_node(super_user,
                                             node_sub_id,
                                             "outputVariablesMapping").body["outputVariablesMapping"]
    automap_result_for_input = automap_node(super_user,
                                            node_sub_id,
                                            "inputVariablesMapping").body["inputVariablesMapping"]
    sub_node.properties["inputVariablesMapping"] = automap_result_for_input
    sub_node.properties["outputVariablesMapping"] = automap_result_for_output
    upd_body = NodeUpdateDto.construct(**sub_node.dict(), diagramVersionId=temp_version_id)
    update_node(super_user,
                node_id=node_sub_id,
                body=upd_body)
    sub_node_info = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                        node_sub_id).body)
    diagram_name = "kk_autotest_diagram_subd_in_subd" + generate_string()
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, diagram_name, '').body
    return {"main_diagram_id": diagram_id, "diagram_name": diagram_name}
