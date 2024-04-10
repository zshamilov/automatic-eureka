import uuid

from typing import List

from products.Decision.framework.model import NodeMetaInfo, Position, CommunicationHubRead, NodeUpdateDto, \
    NodeMappingVariable, EmbedEnum, CommunicationHub, VariablePropertiesBase


def commhub_read_construct(diagram_vers_id, output_var_name, output_var_type_id, service_id, service_version_id,
                           client_id_var_name=None, client_id_type_id=None, input_vars=None, is_control_groop=True,
                           is_target_groop=True, source=None, channel=None, embed: List[EmbedEnum] = None,
                           created_before=None, created_after=None, client_id_type=None, param_id=None,
                           client_v_param_id=None,
                           node_name="Выгрузка задач из Communication Hub", x=400, y=200, valid_flag=True):
    channels = None
    if input_vars is None:
        input_vars = []
    if channel is not None:
        channels = []
        for ch in channel:
            channels.append(ch)
    position = NodeMetaInfo(position=Position(x=x, y=y))
    row_key = str(uuid.uuid4())
    output_var = NodeMappingVariable.construct(rowKey=row_key,
                                               variableName=output_var_name,
                                               typeId=output_var_type_id,
                                               dictId=None,
                                               isArray=True,
                                               isComplex=True,
                                               isDict=False,
                                               variablePath=None,
                                               variableRootId=None,
                                               nodeVariable=None,
                                               id=param_id,
                                               externalId=None)
    client_id = None
    if client_id_var_name is not None:
        client_id = VariablePropertiesBase.construct(rowKey=row_key,
                                                     variableName=client_id_var_name,
                                                     typeId=client_id_type_id,
                                                     dictId=None,
                                                     isArray=False,
                                                     isComplex=False,
                                                     isDict=False,
                                                     variablePath=None,
                                                     variableRootId=None,
                                                     id=client_v_param_id
                                                     )
    properties = CommunicationHubRead.construct(serviceId=service_id,
                                                versionId=service_version_id,
                                                outputVariableMapping=output_var,
                                                inputVariablesMapping=input_vars,
                                                clientId=client_id,
                                                clientIdType=client_id_type,
                                                createdAtAfter=created_after,
                                                createdAtBefore=created_before,
                                                isControlGroup=is_control_groop,
                                                isTargetGroup=is_target_groop,
                                                source=source,
                                                channel=channels,
                                                embed=embed)
    node = NodeUpdateDto.construct(nodeTypeId=24,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node


def commhub_write_construct(diagram_vers_id, input_var_name, input_var_type_id, input_var_id,
                            service_id, service_version_id,
                            node_variable="task_root",
                            input_vars=None, output_vars=None, path_params_vars=None,
                            node_name="Отправка задач в Communication Hub", x=400, y=200, valid_flag=True):
    if input_vars is None:
        input_vars = []
    if output_vars is None:
        output_vars = []
    if path_params_vars is None:
        path_params_vars = []
    position = NodeMetaInfo(position=Position(x=x, y=y))
    row_key = str(uuid.uuid4())
    input_var = NodeMappingVariable.construct(rowKey=row_key,
                                              variableName=input_var_name,
                                              typeId=input_var_type_id,
                                              dictId=None,
                                              isArray=False,
                                              isComplex=True,
                                              isDict=False,
                                              variablePath=None,
                                              variableRootId=None,
                                              nodeVariable=node_variable,
                                              id=input_var_id)
    properties = CommunicationHub.construct(serviceId=service_id,
                                            versionId=service_version_id,
                                            inputVariableMapping=input_var,
                                            outputVariablesMapping=output_vars,
                                            inputVariablesMapping=input_vars,
                                            pathParameterVariablesMapping=path_params_vars)
    node = NodeUpdateDto.construct(nodeTypeId=23,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node
