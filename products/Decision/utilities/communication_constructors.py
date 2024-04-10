from products.Decision.framework.model import CommunicationChannelCreateDto, CommunicationVariableViewWithoutIdDto, \
    CommunicationChannelCreateUserVersionDto, CommunicationChannelUpdateDto


def communication_var_construct(variable_name,
                                script_var_name,
                                data_source_type,
                                primitive_type_id=None,
                                ctype_version_id=None,
                                array_flag=False,
                                min_value=None,
                                max_value=None,
                                max_size=None,
                                dict_id=None,
                                dynamic_list_type=None,
                                mandatory_flag=False):
    return CommunicationVariableViewWithoutIdDto.construct(variableName=variable_name,
                                                           scriptVariableName=script_var_name,
                                                           primitiveTypeId=primitive_type_id,
                                                           complexTypeVersionId=ctype_version_id,
                                                           arrayFlag=array_flag,
                                                           dataSourceType=data_source_type,
                                                           minValue=min_value,
                                                           maxValue=max_value,
                                                           maxSize=max_size,
                                                           dictionaryId=dict_id,
                                                           dynamicListType=dynamic_list_type,
                                                           mandatoryFlag=mandatory_flag)


def communication_construct(communication_channel_name,
                            script_version_id,
                            communication_variables=None,
                            description=None,
                            catalog_id=None):
    return CommunicationChannelCreateDto.construct(objectName=communication_channel_name,
                                                   description=description,
                                                   scriptVersionId=script_version_id,
                                                   communicationVariables=communication_variables,
                                                   catalogId=catalog_id)


def update_channel_construct(communication_channel_name,
                             script_version_id,
                             communication_variables=None,
                             description=None):
    return CommunicationChannelUpdateDto.construct(objectName=communication_channel_name,
                                                   description=description,
                                                   scriptVersionId=script_version_id,
                                                   communicationVariables=communication_variables)


def channel_user_version_construct(communication_channel_name,
                                   script_version_id,
                                   communication_variables=None,
                                   description=None,
                                   version_name=None,
                                   version_description=None):
    return CommunicationChannelCreateUserVersionDto(objectName=communication_channel_name,
                                                    versionName=version_name,
                                                    versionDescription=version_description,
                                                    description=description,
                                                    scriptVersionId=script_version_id,
                                                    communicationVariables=communication_variables)
