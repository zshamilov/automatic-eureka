from products.Decision.framework.model import OfferCreateDto, OfferVariableWithoutIdDto, OfferUpdateDto, \
    OfferVariableFullViewDto, OfferCreateUserVersionDto


def offer_construct(offer_name,
                    script_version_id,
                    script_id,
                    script_name,
                    offer_complex_type_version_id,
                    offer_variables=None,
                    op="create",
                    version_name=None,
                    version_description=None,
                    catalog_id=None,
                    offer_id=None,
                    offer_vers_id=None):
    if op == "create":
        return OfferCreateDto.construct(objectName=offer_name,
                                        scriptVersionId=script_version_id,
                                        scriptId=script_id,
                                        scriptName=script_name,
                                        offerComplexTypeVersionId=offer_complex_type_version_id,
                                        offerVariables=offer_variables,
                                        catalogId=catalog_id)
    if op == "update":
        return OfferUpdateDto.construct(objectName=offer_name,
                                        scriptVersionId=script_version_id,
                                        scriptId=script_id,
                                        scriptName=script_name,
                                        offerComplexTypeVersionId=offer_complex_type_version_id,
                                        offerVariables=offer_variables,
                                        versionId=offer_vers_id)
    if op == "create_user_version":
        return OfferCreateUserVersionDto.construct(objectName=offer_name,
                                                   scriptVersionId=script_version_id,
                                                   scriptName=script_name,
                                                   scriptId=script_id,
                                                   offerComplexTypeVersionId=offer_complex_type_version_id,
                                                   versionName=version_name,
                                                   versionDescription=version_description,
                                                   offerVariables=offer_variables,
                                                   id=offer_id)


def offer_variable_construct(variable_name,
                             script_variable_name,
                             array_flag,
                             data_source_type,
                             mandatory_flag,
                             primitive_type_id=None,
                             complex_type_version_id=None,
                             min_value=None,
                             max_value=None,
                             max_size=None,
                             dictionary_id=None,
                             dynamic_list_type=None,
                             variable_id=None,
                             op="create"):
    if op == "create":
        return OfferVariableWithoutIdDto.construct(variableName=variable_name,
                                                   scriptVariableName=script_variable_name,
                                                   primitiveTypeId=primitive_type_id,
                                                   complexTypeVersionId=complex_type_version_id,
                                                   arrayFlag=array_flag,
                                                   dataSourceType=data_source_type,
                                                   minValue=min_value,
                                                   maxValue=max_value,
                                                   maxSize=max_size,
                                                   dictionaryId=dictionary_id,
                                                   dynamicListType=dynamic_list_type,
                                                   mandatoryFlag=mandatory_flag)
    if op == "update":
        return OfferVariableFullViewDto.construct(variableName=variable_name,
                                                  scriptVariableName=script_variable_name,
                                                  primitiveTypeId=primitive_type_id,
                                                  complexTypeVersionId=complex_type_version_id,
                                                  arrayFlag=array_flag,
                                                  dataSourceType=data_source_type,
                                                  minValue=min_value,
                                                  maxValue=max_value,
                                                  maxSize=max_size,
                                                  dictionaryId=dictionary_id,
                                                  dynamicListType=dynamic_list_type,
                                                  mandatoryFlag=mandatory_flag,
                                                  id=variable_id)
