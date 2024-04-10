import uuid
from typing import Union, List

from products.Decision.framework.model import NodeMetaInfo, Position, NodeUpdateDto, \
    NodeMappingVariable, PolicyRead, VariablePropertiesBase, DiagramInOutParameterFullViewDto, \
    DiagramInnerVariableFullViewDto, ExternalServiceTechFullViewDto, AdditionalParameters, ContactDateTimeNodeVariable
from products.Decision.utilities.custom_models import SystemCTypes, IntNodeType


def policy_node_construct(diagram_vers_id,
                          node_output_var: Union[DiagramInOutParameterFullViewDto, DiagramInnerVariableFullViewDto],
                          client_id_var: Union[DiagramInOutParameterFullViewDto, DiagramInnerVariableFullViewDto],
                          ext_service: ExternalServiceTechFullViewDto,
                          dry_run: bool = False,
                          weak: bool = False,
                          contact_date_time: str = None,
                          additional_parameters: List[AdditionalParameters] = None,
                          node_name="RTF-Policy. Проверка контактной политики", x=900, y=200, valid_flag=True):
    # так как при передаче contactDateTime не может быть мгновенного времени отправки - флаг приобретает
    # противоположное значение
    is_instant_dispatch = not contact_date_time

    contact_dt_node_var: ContactDateTimeNodeVariable = ContactDateTimeNodeVariable.construct(expression=contact_date_time,
                                                                                             functionIds=[])

    position = NodeMetaInfo(position=Position(x=x, y=y))

    policy_var = VariablePropertiesBase.construct(rowKey=str(uuid.uuid4()),
                                                  variableName=node_output_var.parameterName,
                                                  typeId=node_output_var.typeId,
                                                  dictId=node_output_var.dictId,
                                                  isArray=node_output_var.arrayFlag,
                                                  isComplex=node_output_var.complexFlag,
                                                  isDict=node_output_var.dictFlag,
                                                  variablePath=None,
                                                  variableRootId=None,
                                                  id=node_output_var.parameterId)

    client_id_node_var = VariablePropertiesBase.construct(rowKey=str(uuid.uuid4()),
                                                          variableName=client_id_var.parameterName,
                                                          typeId=client_id_var.typeId,
                                                          dictId=client_id_var.dictId,
                                                          isArray=client_id_var.arrayFlag,
                                                          isComplex=client_id_var.complexFlag,
                                                          isDict=client_id_var.dictFlag,
                                                          variablePath=None,
                                                          variableRootId=None,
                                                          id=client_id_var.parameterId)

    properties = PolicyRead.construct(serviceId=ext_service.serviceId,
                                      versionId=ext_service.versionId,
                                      outputVariableMapping=policy_var,
                                      clientId=client_id_node_var,
                                      dryRun=dry_run,
                                      weak=weak,
                                      isInstantDispatch=is_instant_dispatch,
                                      contactDateTime=contact_dt_node_var,
                                      additionalParameters=additional_parameters)
    node = NodeUpdateDto.construct(nodeTypeId=IntNodeType.policyRead.value,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node
