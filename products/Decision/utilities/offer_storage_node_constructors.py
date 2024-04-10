import uuid

from products.Decision.framework.model import NodeMetaInfo, Position, NodeUpdateDto, \
    NodeMappingVariable, OfferStorageWrite, OfferStorageRead
from products.Decision.utilities.custom_models import IntNodeType


def os_write_construct(diagram_vers_id, output_var_name, output_var_type_id, service_id, service_version_id,
                       node_variable="offers", continue_flg=False, path_parameter_var_map=None, param_id=None,
                       node_name="Отправка предложений в Offer Storage", x=400, y=200, valid_flag=True):
    if path_parameter_var_map is None:
        path_parameter_var_map = []
    position = NodeMetaInfo(position=Position(x=x, y=y))
    row_key = str(uuid.uuid4())
    offer_var = NodeMappingVariable.construct(rowKey=row_key,
                                              variableName=output_var_name,
                                              typeId=output_var_type_id,
                                              dictId=None,
                                              isArray=True,
                                              isComplex=True,
                                              isDict=False,
                                              variablePath=None,
                                              variableRootId=None,
                                              nodeVariable=node_variable,
                                              id=param_id,
                                              externalId=None)
    properties = OfferStorageWrite.construct(serviceId=service_id,
                                             versionId=service_version_id,
                                             offerVariableMapping=offer_var,
                                             continueWithPartialWrittenOffers=continue_flg,
                                             pathParameterVariablesMapping=path_parameter_var_map)
    node = NodeUpdateDto.construct(nodeTypeId=IntNodeType.offerStorageWrite.value,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node


def os_read_client_construct(diagram_vers_id, service_id, service_version_id, client_id_type,
                             client_var_name, client_var_type_id, output_var_name, output_var_type_id,
                             service_type="OFFER_STORAGE_READ_BY_CLIENT_ID", node_variable="offer_storage_read_response",
                             ext_offer_id_var_name=None, ext_offer_id_var_type=None, active_channel_flag=False,
                             active_flag=False, control_flag=False, default_offers_flag=False, offer_count=None,
                             param_id=None, client_v_param_id=None, ext_offer_id_v_param_id=None,
                             node_name="Выгрузка предложений из Offer Storage", x=400, y=200, valid_flag=True):
    position = NodeMetaInfo(position=Position(x=x, y=y))
    row_key = str(uuid.uuid4())
    offer_read_out_var_mapping = NodeMappingVariable.construct(rowKey=row_key,
                                                               variableName=output_var_name,
                                                               typeId=output_var_type_id,
                                                               dictId=None,
                                                               isArray=True,
                                                               isComplex=True,
                                                               isDict=False,
                                                               variablePath=None,
                                                               variableRootId=None,
                                                               nodeVariable=node_variable,
                                                               id=param_id)
    external_offer_id = None
    if ext_offer_id_var_name is not None:
        external_offer_id = NodeMappingVariable.construct(rowKey=row_key,
                                                          variableName=ext_offer_id_var_name,
                                                          typeId=ext_offer_id_var_type,
                                                          dictId=None,
                                                          isArray=False,
                                                          isComplex=False,
                                                          isDict=False,
                                                          variablePath=None,
                                                          variableRootId=None,
                                                          nodeVariable=None,
                                                          externalId=None,
                                                          id=ext_offer_id_v_param_id)
    client_id = NodeMappingVariable.construct(rowKey=row_key,
                                              variableName=client_var_name,
                                              typeId=client_var_type_id,
                                              dictId=None,
                                              isArray=False,
                                              isComplex=False,
                                              isDict=False,
                                              variablePath=None,
                                              variableRootId=None,
                                              nodeVariable=None,
                                              id=client_v_param_id)
    properties = OfferStorageRead.construct(serviceId=service_id,
                                            versionId=service_version_id,
                                            serviceType=service_type,
                                            offerReadOutputVariableMapping=offer_read_out_var_mapping,
                                            externalOfferId=external_offer_id,
                                            clientId=client_id,
                                            clientIdType=client_id_type,
                                            activeChannel=active_channel_flag,
                                            active=active_flag,
                                            control=control_flag,
                                            getDefaultOffers=default_offers_flag,
                                            offerCount=offer_count)
    node = NodeUpdateDto.construct(nodeTypeId=25,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node


def os_read_offer_construct(diagram_vers_id, service_id, service_version_id, output_var_name, output_var_type_id,
                            ext_offer_id_var_name, ext_offer_id_var_type, ext_offer_node_var="offerId",
                            client_id_type=None, service_type="OFFER_STORAGE_READ_BY_OFFER_ID",
                            node_variable="offer_storage_read_response", active_channel_flag=False,
                            active_flag=False, control_flag=False, default_offers_flag=False, offer_count=None,
                            param_id=None, ext_offer_id_v_param_id=None,
                            node_name="Выгрузка предложений из Offer Storage", x=400, y=200, valid_flag=True):
    position = NodeMetaInfo(position=Position(x=x, y=y))
    row_key = str(uuid.uuid4())
    offer_read_out_var_mapping = NodeMappingVariable.construct(rowKey=row_key,
                                                               variableName=output_var_name,
                                                               typeId=output_var_type_id,
                                                               dictId=None,
                                                               isArray=True,
                                                               isComplex=True,
                                                               isDict=False,
                                                               variablePath=None,
                                                               variableRootId=None,
                                                               nodeVariable=node_variable,
                                                               id=param_id)
    external_offer_id = NodeMappingVariable.construct(rowKey=row_key,
                                                      variableName=ext_offer_id_var_name,
                                                      typeId=ext_offer_id_var_type,
                                                      dictId=None,
                                                      isArray=False,
                                                      isComplex=False,
                                                      isDict=False,
                                                      variablePath=None,
                                                      variableRootId=None,
                                                      nodeVariable=ext_offer_node_var,
                                                      id=ext_offer_id_v_param_id)
    client_id = None
    properties = OfferStorageRead.construct(serviceId=service_id,
                                            versionId=service_version_id,
                                            serviceType=service_type,
                                            offerReadOutputVariableMapping=offer_read_out_var_mapping,
                                            externalOfferId=external_offer_id,
                                            clientId=client_id,
                                            clientIdType=client_id_type,
                                            activeChannel=active_channel_flag,
                                            active=active_flag,
                                            control=control_flag,
                                            getDefaultOffers=default_offers_flag,
                                            offerCount=offer_count)
    node = NodeUpdateDto.construct(nodeTypeId=25,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node
