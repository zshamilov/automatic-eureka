import uuid
from typing import List

from products.Decision.framework.model import NodeValidateDto, NodesCopyDto, NodesPasteRequestDto, Position, \
    VariableViewDto, \
    NodeUpdateDto, NodeRemapDto, ExternalService, NodeViewWithVariablesDto, NodeAutoMappingDto
from products.Decision.framework.scheme.decision_scheme_nodes import DecisionNodes
from products.Decision.utilities.node_cunstructors import external_service_properties
from sdk.user import User


def create_node(user: User, body):
    return user.with_api.send(DecisionNodes.create_node(body=body))


def create_link(user: User, body):
    return user.with_api.send(DecisionNodes.create_link(body=body))


def get_node_by_id(user: User, node_id):
    return user.with_api.send(DecisionNodes.get_node(node_id=node_id))


def delete_node_by_id(user: User, node_id):
    return user.with_api.send(DecisionNodes.delete_node(node_id=node_id))


def delete_link_by_id(user: User, link_id):
    return user.with_api.send(DecisionNodes.delete_link(link_id=link_id))


def check_out_var(body, added_vars: list = None):
    if added_vars is None:
        added_vars = []
    possible_mappings = ['outputVariablesMapping', 'calculate', 'ruleVariable', 'outputVariable']
    for mapping in possible_mappings:
        out_mapping = getattr(body.properties, mapping, None)
        if out_mapping is not None:
            if not isinstance(out_mapping, list):
                out_mapping: VariableViewDto
                if out_mapping.id is None and not getattr(out_mapping, 'isLiteral', False):
                    added_vars.append(VariableViewDto.construct(variableName=out_mapping.variableName,
                                                                typeId=out_mapping.typeId,
                                                                dictId=out_mapping.dictId,
                                                                isComplex=out_mapping.isComplex,
                                                                isDict=out_mapping.isDict,
                                                                isArray=out_mapping.isArray,
                                                                variableRootId=out_mapping.variableRootId,
                                                                variablePath=out_mapping.variablePath))
            elif len(out_mapping) > 0:
                for v in out_mapping:
                    v: VariableViewDto
                    if v.id is None and getattr(v, 'nodeVariable', None) != "externalServiceStatusCode" \
                            and not getattr(v, 'isLiteral', False):
                        added_vars.append(VariableViewDto.construct(variableName=v.variableName,
                                                                    typeId=v.typeId,
                                                                    dictId=v.dictId,
                                                                    isComplex=v.isComplex,
                                                                    isDict=v.isDict,
                                                                    isArray=v.isArray,
                                                                    variableRootId=v.variableRootId,
                                                                    variablePath=v.variablePath))
    return added_vars


def update_node(user: User, node_id, body: NodeUpdateDto, validate_body: NodeValidateDto = None):
    added_vars: List[VariableViewDto] = []
    if validate_body is not None:
        if validate_body.addedVariables is None:
            validate_body.addedVariables = []
        valid_resp = user.with_api.send(DecisionNodes.put_node_validate(
            node_id=node_id, body=validate_body))
        if valid_resp.body["httpCode"] == 422:
            body.validFlag = False
            print(body.validFlag)
    else:
        added_vars = check_out_var(body)
        valid_resp = user.with_api.send(DecisionNodes.put_node_validate(
            node_id=node_id, body=NodeValidateDto.construct(
                nodeTypeId=body.nodeTypeId,
                properties=body.properties,
                addedVariables=added_vars)))
        if valid_resp.body["httpCode"] == 422:
            body.validFlag = False
            print(body.validFlag)
        elif valid_resp.body["httpCode"] == 200:
            body.validFlag = True
            print(body.validFlag)
    body.addedVariables = added_vars
    return user.with_api.send(DecisionNodes.put_update_node(node_id=node_id, body=body))


def validate_node(user: User, node_id, body: NodeValidateDto):
    added_vars: List[VariableViewDto] = check_out_var(body)
    body.addedVariables = added_vars
    return user.with_api.send(DecisionNodes.put_node_validate(node_id=node_id, body=body))


def previous_nodes(user: User, node_id, query):
    return user.with_api.send(DecisionNodes.get_previous_nodes(node_id=node_id, query=query))


def possible_nodes(user: User, node_id, query):
    return user.with_api.send(DecisionNodes.get_possible_nodes(node_id=node_id, query=query))


def remap_node(user: User, node_id, body):
    return user.with_api.send(DecisionNodes.put_remap_node(node_id=node_id, body=body))


def remap_external_service_node(user: User, node_id, service_id, service_version_id, propeties: ExternalService = None):
    if propeties is None:
        propeties = external_service_properties(service_id="", version_id="",
                                                input_variables_mapping=[], output_variables_mapping=[])
    body: NodeRemapDto = NodeRemapDto(nodeTypeId=8, objectId=service_id,
                                      objectVersionId=service_version_id, properties=propeties)
    response = user.with_api.send(DecisionNodes.put_remap_node(node_id=node_id, body=body))
    return ExternalService(**response.body)


def copy_nodes(user: User, version_id: [str, uuid], node_ids: list, link_ids=None):
    link_ids = link_ids or []
    body = NodesCopyDto.construct(diagramVersionId=str(version_id),
                                  nodeIds=node_ids,
                                  linkIds=link_ids)
    return user.with_api.send(DecisionNodes.post_copy_nodes(body=body))


def paste_nodes(user: User, copy_id: [str, uuid], version_id: [str, uuid], x_pos: float = 777, y_pos: float = 777):
    body = NodesPasteRequestDto.construct(copyId=str(copy_id),
                                          diagramVersionId=version_id,
                                          position=Position.construct(x=x_pos,
                                                                      y=y_pos))
    return user.with_api.send(DecisionNodes.post_paste_nodes(body=body))


def revalidate_node(user: User, diagram_version_id):
    return user.with_api.send(DecisionNodes.post_revalidate_nodes(diagram_version_id=diagram_version_id))


def automap_node(user: User, node_id, map_collection_name: str, skip_automap_ids: list = None,
                 force_automap_ids: list = None):
    node = NodeViewWithVariablesDto.construct(**get_node_by_id(user, node_id).body)
    node_type_id = node.nodeTypeId
    node_properties = node.properties
    body = NodeAutoMappingDto.construct(collectionName=map_collection_name,
                                        nodeTypeId=node_type_id,
                                        properties=node_properties,
                                        skipAutoMappingVariableIds=skip_automap_ids,
                                        forceAutoMappingVariableIds=force_automap_ids
                                        )
    return user.with_api.send(DecisionNodes.put_automap_node(node_id=node_id, body=body))
