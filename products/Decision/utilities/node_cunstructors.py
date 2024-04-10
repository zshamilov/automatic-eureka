import uuid

from products.Decision.framework.model import CustomCode, Position, NodeMetaInfo, NodeUpdateDto, Calculates, Finish, \
    Start, NodeCreateDto, NodeMappingVariable, CalculateExpression, CalculateNodeVariable, OutParameterShortInfo, \
    FinishNodeVariable, StartNodeVariable, LinkCreateDto, Subdiagram, SubDiagramOutVariableMapping, \
    Branch, Fork, DefaultBranch, JoinFlow, RulesetVariableProperties, RulesetProperties, Ruleset, \
    ExternalService, OfferNodeMappingVariable, TemplateMappingVariable, \
    Offer, ReadMappingVariable, JdbcRead, AggregateComputeProperties, \
    AggregateComputeOutputVariableMapping, GroupingElementsMapping, AggregateCompute, RetentionType, RetentionTimeUnit, \
    BranchNodeBranch, BranchNode, Scorecard, ScorecardOutputVariable, ScorecardInputVariable, ScoreValue, \
    WriteReadVariableProperties, WriteNodeVariableMapping, DataSourceVariable, JdbcWrite, Communication, NodeRemapDto, \
    WriteFilterVariableProperties, ChannelNodeMappingVariable, TarantoolReadInputMappingVariable, \
    TarantoolReadByIndexInputMappingVariable
from products.Decision.utilities.custom_models import IntNodeType


def aggregate_properties(aggregate_id,
                         aggregate_version_id,
                         diagram_aggregate_element,
                         is_used_in_diagram,
                         aggregate_element_type_id=None,
                         aggregate_function=None):
    return AggregateComputeProperties.construct(aggregateId=aggregate_id,
                                                versionId=aggregate_version_id,
                                                diagramAggregateElement=diagram_aggregate_element,
                                                aggregateElementTypeId=aggregate_element_type_id,
                                                isUsedInDiagram=is_used_in_diagram,
                                                aggregateFunction=aggregate_function)


def aggregate_compute_out_var(is_arr, is_compl,
                              aggregate, is_dict=False,
                              var_name=None, type_id=None,
                              dict_id=None, var_path=None,
                              var_root_id=None, row_key=None,
                              param_id=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return AggregateComputeOutputVariableMapping.construct(variableName=var_name,
                                                           typeId=type_id,
                                                           dictId=dict_id,
                                                           isArray=is_arr,
                                                           isComplex=is_compl,
                                                           isDict=is_dict,
                                                           variablePath=var_path,
                                                           variableRootId=var_root_id,
                                                           aggregate=aggregate,
                                                           rowKey=row_key,
                                                           id=param_id)


def grouping_element_map(aggregate_element, diagram_element, full_path_value=None,
                         simple_name_value=None, column=None):
    return GroupingElementsMapping(aggregateElement=aggregate_element,
                                   diagramElement=diagram_element)


def aggregate_compute_properties(output_vars, retention_type: RetentionType,
                                 retention_time_value: int, retention_time_unit: RetentionTimeUnit,
                                 grouping_elements=None, retention_time_field=None,
                                 watermark_type=None, duration=None, coefficient=None):
    return AggregateCompute.construct(groupingElements=grouping_elements,
                                      outputVariablesMapping=output_vars,
                                      retentionTimeField=retention_time_field,
                                      retentionType=retention_type,
                                      retentionTimeValue=retention_time_value,
                                      retentionTimeUnit=retention_time_unit,
                                      watermarkType=watermark_type,
                                      duration=duration,
                                      coefficient=coefficient)


def aggregate_compute_node_construct(x, y, temp_version_id, properties=None,
                                     operation="create", node_name_up=None, descr_up=None,
                                     valid_flag=True):
    node = None
    node_name = "Расчет агрегата"
    int_node_type = 11
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def tarantool_read_input_var(var_name, type_id, providers_column_name,
                             providers_column_data_type, providers_column_is_null=None, is_dict: bool = False,
                             is_arr: bool = False, is_compl: bool = False,
                             var_path=None, var_root_id=None, dict_id=None, is_null=None, row_key=None, param_id=None,
                             is_literal=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    node_var = DataSourceVariable(columnName=providers_column_name,
                                  dataType=providers_column_data_type,
                                  isNullable=providers_column_is_null)
    return TarantoolReadInputMappingVariable(variableName=var_name,
                                             typeId=type_id,
                                             dictId=dict_id,
                                             isArray=is_arr,
                                             isComplex=is_compl,
                                             isDict=is_dict,
                                             isLiteral=is_literal,
                                             variablePath=var_path,
                                             variableRootId=var_root_id,
                                             nodeVariable=node_var,
                                             isNullValue=is_null,
                                             rowKey=row_key,
                                             id=param_id)


def tarantool_read_index_var(index_name, predicate, order, input_vars_mapping, row_key=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return TarantoolReadByIndexInputMappingVariable(rowKey=row_key,
                                                    indexName=index_name,
                                                    predicate=predicate,
                                                    order=order,
                                                    inputVariablesMapping=input_vars_mapping)


def insert_input_var_mapping(var_name, type_id, providers_column_name,
                             providers_column_data_type, is_dict: bool = False,
                             is_arr: bool = False, is_compl: bool = False,
                             simple_name_val=None, full_path_val=None,
                             var_path=None, var_root_id=None,
                             column=None, dict_id=None, is_null=None,
                             array_var_name=None, array_var_path=None, row_key=None, param_id=None, is_literal=None,
                             is_primary=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    array_var = None
    if array_var_name is not None and array_var_path is not None:
        array_var = WriteReadVariableProperties(variableName=array_var_name,
                                                variablePath=array_var_path)
    node_var = DataSourceVariable(columnName=providers_column_name,
                                  dataType=providers_column_data_type,
                                  isNullable=is_null,
                                  isPrimary=is_primary)
    return WriteNodeVariableMapping(variableName=var_name,
                                    typeId=type_id,
                                    dictId=dict_id,
                                    isArray=is_arr,
                                    isComplex=is_compl,
                                    isDict=is_dict,
                                    variablePath=var_path,
                                    variableRootId=var_root_id,
                                    arrayVariable=array_var,
                                    nodeVariable=node_var,
                                    rowKey=row_key,
                                    id=param_id,
                                    isLiteral=is_literal)


def insert_filter_vars(var_name, is_arr: bool, is_compl: bool,
                       type_id, expression,
                       filter_sign, is_dict: bool = False,
                       var_path=None, var_root_id=None, dict_id=None,
                       array_var_name=None, array_var_path=None, row_key=None, param_id=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    array_var = None
    if array_var_name is not None and array_var_path is not None:
        array_var = WriteReadVariableProperties(variableName=array_var_name,
                                                variablePath=array_var_path)
    return WriteFilterVariableProperties.construct(rowKey=row_key,
                                                   variableName=var_name,
                                                   typeId=type_id,
                                                   dictId=dict_id,
                                                   isArray=is_arr,
                                                   isComplex=is_compl,
                                                   isDict=is_dict,
                                                   variablePath=var_path,
                                                   variableRootId=var_root_id,
                                                   expression=expression,
                                                   filterSign=filter_sign,
                                                   arrayVariable=array_var,
                                                   id=param_id)


def insert_node_properties(source_id: str, table_name: str, query_type: str,
                           schema_name=None,
                           input_vars_update_mapping=None,
                           filter_variables=None,
                           input_vars_condition_mapping=None,
                           array_flag=False):
    if input_vars_update_mapping is None:
        input_vars_update_mapping = []
    if input_vars_condition_mapping is None:
        input_vars_condition_mapping = []
    if filter_variables is None:
        filter_variables = []
    return JdbcWrite.construct(dataProviderUuid=source_id,
                               tableName=table_name,
                               schemaName=schema_name,
                               queryType=query_type,
                               arrayFlag=array_flag,
                               inputVariablesUpdateMapping=input_vars_update_mapping,
                               inputVariablesConditionMapping=input_vars_condition_mapping,
                               filterVariables=filter_variables)


def insert_node_construct(x, y, temp_version_id, properties=None,
                          operation="create", node_name_up=None, descr_up=None,
                          valid_flag=True):
    node = None
    node_name = "Сохранение данных"
    int_node_type = 5
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def read_variable(is_arr, is_compl, is_dict,
                  var_name=None,
                  type_id=None,
                  dict_id=None,
                  var_path=None,
                  var_root_id=None,
                  node_variable=None,
                  is_jdbc_arr_key=None,
                  array_var=None,
                  row_key=None,
                  v_id=None,
                  node_variable_type=None,
                  param_id=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return ReadMappingVariable.construct(variableName=var_name,
                                         typeId=type_id,
                                         dictId=dict_id,
                                         isArray=is_arr,
                                         isComplex=is_compl,
                                         isDict=is_dict,
                                         variablePath=var_path,
                                         variableRootId=var_root_id,
                                         nodeVariable=node_variable,
                                         externalId=v_id,
                                         id=param_id,
                                         isJdbcArrayKey=is_jdbc_arr_key,
                                         arrayVariable=array_var,
                                         rowKey=row_key,
                                         nodeVariableType=node_variable_type)


def read_array_variable(var_name=None, var_path=None):
    return WriteReadVariableProperties.construct(variableName=var_name,
                                                 variablePath=var_path)


def offer_variable(var_id, value=None,
                   display_name=None,
                   row_key=None,
                   variable_name=None,
                   type_id=None,
                   d_source_type=None,
                   dict_id=None,
                   dynamic_list_type=None,
                   mandatory_flag=None,
                   min_val=None,
                   max_val=None,
                   max_size=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return TemplateMappingVariable.construct(id=var_id,
                                             value=value,
                                             displayName=display_name,
                                             rowKey=row_key,
                                             variableName=variable_name,
                                             primitiveTypeId=type_id,
                                             dataSourceType=d_source_type,
                                             dictionaryId=dict_id,
                                             dynamicListType=dynamic_list_type,
                                             mandatoryFlag=mandatory_flag,
                                             minValue=min_val,
                                             maxValue=max_val,
                                             maxSize=max_size)


def ext_serv_var(var_type, is_arr, is_compl, name,
                 type_id, service_variable_id, var_path=None, var_root_id=None,
                 node_variable=None, is_dict=False, dict_id=None, row_key=None, param_id=None,
                 is_literal=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    if var_type == "in":
        return NodeMappingVariable.construct(rowKey=row_key,
                                             variableName=name,
                                             typeId=type_id,
                                             dictId=dict_id,
                                             isArray=is_arr,
                                             isComplex=is_compl,
                                             isDict=is_dict,
                                             isLiteral=is_literal,
                                             variablePath=var_path,
                                             variableRootId=var_root_id,
                                             nodeVariable=node_variable,
                                             externalId=service_variable_id,
                                             id=param_id)
    if var_type == "out":
        return NodeMappingVariable.construct(rowKey=row_key,
                                             variableName=name,
                                             typeId=type_id,
                                             dictId=dict_id,
                                             isArray=is_arr,
                                             isComplex=is_compl,
                                             isDict=is_dict,
                                             variablePath=var_path,
                                             variableRootId=var_root_id,
                                             nodeVariable=node_variable,
                                             externalId=service_variable_id,
                                             id=param_id)


def rule_set_var_const(is_arr, is_complex, var_name=None, type_id=None,
                       var_path=None, var_root_id=None, is_dict=False, dict_id=None,
                       row_key=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return RulesetVariableProperties(rowKey=row_key,
                                     variableName=var_name,
                                     typeId=type_id,
                                     isArray=is_arr,
                                     isComplex=is_complex,
                                     isDict=is_dict,
                                     dictId=dict_id,
                                     variablePath=var_path,
                                     variableRootId=var_root_id)


def rule_set_properties(apply_rule=None, rule_name=None, rule_code=None,
                        rule_type_id=None, rule_description=None,
                        rule_expression=None, rule_weight_factor=None, function_ids=None,
                        row_key=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    if function_ids is None:
        function_ids = []
    return RulesetProperties(rowKey=row_key,
                             applyRule=apply_rule,
                             ruleName=rule_name,
                             ruleCode=rule_code,
                             ruleTypeId=rule_type_id,
                             ruleDescription=rule_description,
                             ruleExpression=rule_expression,
                             functionIds=function_ids,
                             ruleWeightFactor=rule_weight_factor)


def branch_node_properties(branching_type, condition, branching_value_type,
                           branches=None, default_path=None):
    return BranchNode.construct(branches=branches,
                                defaultPath=default_path,
                                branchingValueType=branching_value_type,
                                condition=condition,
                                branchingType=branching_type)


def branch(link_id, node_id, operator, value_from,
           value_from_include_flag=None, value_to=None,
           value_to_include_flag=None, row_key=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return BranchNodeBranch.construct(rowKey=row_key,
                                      linkId=link_id,
                                      nodeId=node_id,
                                      operator=operator,
                                      valueFrom=value_from,
                                      valueFromIncludeFlag=value_from_include_flag,
                                      valueTo=value_to,
                                      valueToIncludeFlag=value_to_include_flag)


def default_branch(node_id, link_id="", row_key=None):
    return DefaultBranch(rowKey=row_key,
                         nodeId=node_id,
                         linkId=link_id)


def join_branch(path, priority, row_key=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return Branch.construct(rowKey=row_key,
                            path=path,
                            priority=priority)


def variables_for_node(node_type, is_arr, is_compl, name,
                       type_id=None, vers_id=None, calc_val=None, calc_type_id=None,
                       var_path=None, var_root_id=None, node_variable=None, is_hide=None,
                       param_name=None, is_null_value=False, is_dict=False, dict_id=None,
                       is_variable_from_offer_template=True, outer_variable_id=None, func_ids=None,
                       row_key=None, param_id=None, is_literal=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    if func_ids is None:
        func_ids = []
    var = None
    if vers_id is not None:
        vers_id = str(vers_id)

    if node_type == "start":
        var = StartNodeVariable.construct(rowKey=row_key,
                                          isArray=is_arr,
                                          isComplex=is_compl,
                                          variableName=name,
                                          typeId=str(type_id),
                                          parameterId=str(vers_id),
                                          isDict=is_dict,
                                          dictId=dict_id,
                                          variablePath=var_path,
                                          variableRootId=var_root_id)

    if node_type == "finish":
        var = FinishNodeVariable.construct(rowKey=row_key,
                                           isArray=is_arr,
                                           isComplex=is_compl,
                                           variableName=name,
                                           typeId=str(type_id),
                                           isDict=is_dict,
                                           dictId=dict_id,
                                           id=param_id,
                                           isLiteral=is_literal,
                                           parameter=OutParameterShortInfo.construct(
                                               parameterName=name,
                                               parameterId=vers_id,
                                               isNullValue=is_null_value)
                                           )

    if node_type == "finish_out":
        var = FinishNodeVariable.construct(rowKey=row_key,
                                           isArray=is_arr,
                                           isComplex=is_compl,
                                           variableName=name,
                                           typeId=str(type_id),
                                           isDict=is_dict,
                                           dictId=dict_id,
                                           id=param_id,
                                           isLiteral=is_literal,
                                           parameter=OutParameterShortInfo.construct(
                                               parameterName=param_name,
                                               parameterId=vers_id,
                                               isNullValue=is_null_value)
                                           )

    if node_type == "var_calc":
        var = CalculateNodeVariable.construct(rowKey=row_key,
                                              isArray=is_arr,
                                              isComplex=is_compl,
                                              variableName=name,
                                              typeId=type_id,
                                              variablePath=var_path,
                                              variableRootId=var_root_id,
                                              isDict=is_dict,
                                              dictId=dict_id,
                                              expression=CalculateExpression(calculateExpressionValue=calc_val,
                                                                             functionIds=func_ids))
        if param_id is not None:
            var.id = param_id

    if node_type == "custom_code" or node_type == "comms_out_mapping":
        var = NodeMappingVariable.construct(rowKey=row_key,
                                            variableName=name,
                                            typeId=type_id,
                                            isDict=is_dict,
                                            dictId=dict_id,
                                            isArray=is_arr,
                                            isLiteral=is_literal,
                                            isComplex=is_compl,
                                            variablePath=var_path,
                                            variableRootId=var_root_id,
                                            nodeVariable=node_variable,
                                            externalId=outer_variable_id)
        if param_id is not None:
            var.id = param_id

    if node_type == "subdiagram_input":
        var = NodeMappingVariable.construct(rowKey=row_key,
                                            variableName=name,
                                            typeId=type_id,
                                            isArray=is_arr,
                                            isDict=is_dict,
                                            dictId=dict_id,
                                            isLiteral=is_literal,
                                            isComplex=is_compl,
                                            variablePath=var_path,
                                            variableRootId=var_root_id,
                                            nodeVariable=node_variable,
                                            externalId=outer_variable_id)

    if node_type == "offer_output":
        var = NodeMappingVariable.construct(variableName=name,
                                            typeId=type_id,
                                            isArray=is_arr,
                                            isDict=is_dict,
                                            dictId=dict_id,
                                            isComplex=is_compl,
                                            variablePath=var_path,
                                            variableRootId=var_root_id,
                                            nodeVariable=node_variable,
                                            externalId=outer_variable_id,
                                            rowKey=row_key)

    if node_type == "offer_mapping":
        var = OfferNodeMappingVariable.construct(variableName=name,
                                                 typeId=type_id,
                                                 dictId=dict_id,
                                                 isArray=is_arr,
                                                 isComplex=is_compl,
                                                 isDict=is_dict,
                                                 isLiteral=is_literal,
                                                 variablePath=var_path,
                                                 variableRootId=var_root_id,
                                                 nodeVariable=node_variable,
                                                 isVariableFromTemplate=is_variable_from_offer_template,
                                                 externalId=outer_variable_id,
                                                 rowKey=row_key)

    if node_type == "subdiagram_output":
        var = SubDiagramOutVariableMapping.construct(rowKey=row_key,
                                                     variableName=name,
                                                     typeId=type_id,
                                                     isArray=is_arr,
                                                     isDict=is_dict,
                                                     dictId=dict_id,
                                                     isComplex=is_compl,
                                                     variablePath=var_path,
                                                     variableRootId=var_root_id,
                                                     nodeVariable=node_variable,
                                                     isHide=is_hide,
                                                     externalId=outer_variable_id)

    if param_id is not None:
        var.id = param_id

    return var


def read_properties(data_provider_uuid, query, allow_multi_result_response: bool,
                    out_mapping_vars=None, selected_table_names=None, plain_query=None):
    return JdbcRead.construct(dataProviderUuid=data_provider_uuid,
                              query=query,
                              outputVariablesMapping=out_mapping_vars,
                              selectedTableNames=selected_table_names,
                              allowMultiResultResponse=allow_multi_result_response,
                              plainQuery=plain_query)


def read_node_construct(x, y, temp_version_id, properties=None,
                        operation="create", node_name_up=None, descr_up=None,
                        valid_flag=True):
    node = None
    node_name = "Чтение данных"
    int_node_type = 4
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def offer_properties(offer_id,
                     offer_version_id,
                     offer_variables=None,
                     node_variables_mapping=None,
                     output_variable_mapping=None):
    return Offer.construct(offerId=offer_id,
                           versionId=offer_version_id,
                           offerVariables=offer_variables,
                           nodeVariablesMapping=node_variables_mapping,
                           outputVariableMapping=output_variable_mapping)


def offer_node_construct(x, y, temp_version_id, properties=None,
                         operation="create", node_name_up=None, descr_up=None,
                         node_id=None, valid_flag=True):
    node = None
    node_name = "Предложение"
    int_node_type = 19
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeId=node_id,
                                           nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeId=node_id,
                                           nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def external_service_properties(service_id,
                                version_id,
                                input_variables_mapping,
                                output_variables_mapping,
                                error_variables_mapping=None):
    if error_variables_mapping is None:
        error_variables_mapping = []
    return ExternalService.construct(serviceId=service_id,
                                     versionId=version_id,
                                     inputVariablesMapping=input_variables_mapping,
                                     outputVariablesMapping=output_variables_mapping,
                                     errorVariablesMapping=error_variables_mapping)


def external_service_node_construct(x, y, temp_version_id, properties=None,
                                    operation="create", node_name_up=None, descr_up=None,
                                    valid_flag=True):
    node = None
    node_name = "Вызов внешнего сервиса"
    int_node_type = 8
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def ruleset_node_construct(x, y, temp_version_id,
                           rule_variable=None, rules=None,
                           operation="create", node_name_up=None, descr_up=None,
                           valid_flag=True):
    node = None
    properties = None
    node_name = "Набор правил"
    int_node_type = 7
    if rules is not None:
        properties = Ruleset.construct(ruleVariable=rule_variable, rules=rules)
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def branch_node_construct(x, y, temp_version_id, properties=None, operation="create",
                          node_name_up=None, descr_up=None, valid_flag=True):
    node = None
    node_name = "Ветвление"
    int_node_type = 10
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def fork_node_construct(x, y, temp_version_id, branches=None,
                        default_join_path=None, node_ids_with_join_node_ids=None,
                        operation="create", node_name_up=None, descr_up=None,
                        valid_flag=True):
    node = None
    properties = None
    node_type = "fork"
    node_name = "Распараллеливание потока"
    int_node_type = 17
    if branches is not None:
        properties = Fork.construct(nodeType=None,
                                    branches=branches,
                                    defaultJoinPath=default_join_path,
                                    nodeIdsWithJoinNodeIds=node_ids_with_join_node_ids)
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def join_node_construct(x, y, temp_version_id, branches=None,
                        join_condition_type=None, timeout=None,
                        merge_arrs=False, specify_keys=False, key_var_mapping=None,
                        operation="create", node_name_up=None, descr_up=None,
                        valid_flag=True):
    node = None
    properties = None
    node_type = "join"
    node_name = "Слияние потоков"
    int_node_type = 18
    if branches is not None:
        properties = JoinFlow.construct(nodeType=None,
                                        joinConditionType=join_condition_type,
                                        timeout=timeout,
                                        mergeArrays=merge_arrs,
                                        specifyKeys=specify_keys,
                                        keyVariableMapping=key_var_mapping,
                                        branches=branches)
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def node_construct(x, y, node_type, temp_version_id, variables=None,
                   script_id=None, script_version_id=None, script_type=None,
                   inp_custom_code_vars=None, out_custom_code_vars=None,
                   diagram_id=None, diagram_version_id=None,
                   inp_subdiagram_vars=None, out_subdiagram_vars=None):
    properties = None
    int_node_type = None
    node_name = None
    if node_type == "start":
        node_name = "Начало"
        int_node_type = 2
        properties = Start.construct()
        if variables is not None:
            properties.mappingVariables = variables
        else:
            properties.mappingVariables = []

    if node_type == "finish":
        node_name = "Завершение"
        int_node_type = 3
        if variables is not None:
            properties = Finish.construct()
            properties.mappingVariables = variables

    if node_type == "var_calc":
        node_name = "Расчет переменных"
        int_node_type = 6
        if variables is not None:
            properties = Calculates.construct()
            properties.calculate = variables

    if node_type == "custom_code":
        node_name = "Кастомный код"
        int_node_type = 1
        if inp_custom_code_vars is not None and out_custom_code_vars is not None:
            properties = CustomCode.construct()
            properties.customCodeId = script_id
            properties.scriptType = script_type
            properties.versionId = script_version_id
            properties.inputVariablesMapping = inp_custom_code_vars
            properties.outputVariablesMapping = out_custom_code_vars

    if node_type == "subdiagram":
        node_name = "Поддиаграмма"
        int_node_type = 14
        if inp_subdiagram_vars is not None and out_subdiagram_vars is not None:
            properties = Subdiagram.construct()
            properties.subdiagramId = diagram_id
            properties.versionId = diagram_version_id
            properties.inputVariablesMapping = inp_subdiagram_vars
            properties.outputVariablesMapping = out_subdiagram_vars

    position = NodeMetaInfo(position=Position(x=x, y=y))

    node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                   diagramVersionId=temp_version_id,
                                   nodeName=node_name,
                                   metaInfo=position,
                                   properties=properties)

    return node


def node_update_construct(x, y, node_type, temp_version_id, variables=None,
                          script_id=None, script_version_id=None, script_type=None,
                          inp_custom_code_vars=None, out_custom_code_vars=None,
                          diagram_id=None, diagram_version_id=None,
                          inp_subdiagram_vars=None, out_subdiagram_vars=None,
                          node_name_up=None, descr_up=None, valid_flag=True):
    properties = None
    int_node_type = None
    node_name = None
    if node_type == "start":
        node_name = "Начало"
        int_node_type = 2
        properties = Start.construct()
        if variables is not None:
            properties.mappingVariables = variables
        else:
            properties.mappingVariables = []

    if node_type == "finish":
        node_name = "Завершение"
        int_node_type = 3
        if variables is not None:
            properties = Finish.construct()
            properties.mappingVariables = variables

    if node_type == "var_calc":
        node_name = "Расчет переменных"
        int_node_type = 6
        if variables is not None:
            properties = Calculates.construct()
            properties.calculate = variables

    if node_type == "custom_code":
        node_name = "Кастомный код"
        int_node_type = 1
        if inp_custom_code_vars is not None and out_custom_code_vars is not None:
            properties = CustomCode.construct()
            properties.customCodeId = script_id
            properties.scriptType = script_type
            properties.versionId = script_version_id
            properties.inputVariablesMapping = inp_custom_code_vars
            properties.outputVariablesMapping = out_custom_code_vars

    if node_type == "subdiagram":
        node_name = "Поддиаграмма"
        int_node_type = 14
        if inp_subdiagram_vars is not None and out_subdiagram_vars is not None:
            properties = Subdiagram.construct()
            properties.subdiagramId = diagram_id
            properties.versionId = diagram_version_id
            properties.inputVariablesMapping = inp_subdiagram_vars
            properties.outputVariablesMapping = out_subdiagram_vars

    if node_type == "branch":
        node_name = "Ветвление"
        int_node_type = 10

    position = NodeMetaInfo(position=Position(x=x, y=y))

    if node_name_up is None:
        node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       diagramId=diagram_id,
                                       nodeName=node_name,
                                       nodeDescription=None,
                                       properties=properties,
                                       metaInfo=position,
                                       validFlag=valid_flag)
    else:
        node = NodeUpdateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       diagramId=diagram_id,
                                       nodeName=node_name_up,
                                       nodeDescription=descr_up,
                                       properties=properties,
                                       metaInfo=position,
                                       validFlag=valid_flag)

    return node


def node_remap_construct(int_node_type, object_id, object_version_id, properties):
    return NodeRemapDto.construct(nodeTypeId=int_node_type,
                                  objectId=object_id,
                                  objectVersionId=object_version_id,
                                  properties=properties)


def link_construct(temp_version_id, prev_node_id, next_node_id):
    link = LinkCreateDto.construct(diagramVersionId=temp_version_id,
                                   prevNodeId=prev_node_id,
                                   nextNodeId=next_node_id)

    return link


def score_val_construct(min_value=None, max_value=None,
                        include_min_val=None,
                        include_max_val=None,
                        value=None,
                        score_value=None,
                        row_key=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return ScoreValue.construct(rowKey=row_key,
                                minValue=min_value,
                                maxValue=max_value,
                                includeMinValue=include_min_val,
                                includeMaxValue=include_max_val,
                                value=value,
                                scoreValue=score_value)


def scorecard_input_var(is_arr, is_compl,
                        default_value, is_dict=False, name=None, type_id=None,
                        dict_id=None, var_path=None, var_root_id=None,
                        score_values=None, row_key=None, param_id=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return ScorecardInputVariable.construct(rowKey=row_key,
                                            variableName=name,
                                            typeId=type_id,
                                            dictId=dict_id,
                                            isArray=is_arr,
                                            isComplex=is_compl,
                                            isDict=is_dict,
                                            variablePath=var_path,
                                            variableRootId=var_root_id,
                                            defaultValue=default_value,
                                            scoreValues=score_values,
                                            id=param_id)


def scorecard_output_var(is_arr, is_compl,
                         default_value, is_dict=False, name=None, type_id=None,
                         dict_id=None, var_path=None, var_root_id=None,
                         row_key=None, param_id=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return ScorecardOutputVariable.construct(rowKey=row_key,
                                             variableName=name,
                                             typeId=type_id,
                                             dictId=dict_id,
                                             isArray=is_arr,
                                             isComplex=is_compl,
                                             isDict=is_dict,
                                             variablePath=var_path,
                                             variableRootId=var_root_id,
                                             defaultValue=default_value,
                                             id=param_id)


def scorecard_properties(output_variable, input_variables=None):
    return Scorecard.construct(outputVariable=output_variable,
                               inputVariablesMapping=input_variables)


def scorecard_node_construct(x, y, temp_version_id, properties=None,
                             operation="create", node_name_up=None, descr_up=None,
                             node_id=None, valid_flag=True):
    node = None
    node_name = "Расчет скоркарты"
    int_node_type = 9
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeId=node_id,
                                           nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeId=node_id,
                                           nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node


def comm_var_construct(var_name, var_id, var_value, data_source_type,
                       dynamic_list_type, type_id, display_name=None,
                       dict_id=None, mandatory_flag=False, min_val=None,
                       max_val=None, max_size=None, row_key=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return TemplateMappingVariable.construct(rowKey=row_key, id=var_id, displayName=display_name, value=var_value,
                                             variableName=var_name,
                                             primitiveTypeId=type_id, dataSourceType=data_source_type,
                                             dictionaryId=dict_id,
                                             dynamicListType=dynamic_list_type,
                                             mandatoryFlag=mandatory_flag, minValue=min_val, maxValue=max_val,
                                             maxSize=max_size)


def comm_node_var_construct(var_name, var_id, type_id,
                            node_variable, is_variable_from_channel_template=True, dict_id=None, mandatory_flag=False,
                            row_key=None, is_array=False, is_dict=False, is_complex=False, variable_path=None,
                            variable_root_id=None, param_id=None, is_literal=None):
    if row_key is None:
        row_key = str(uuid.uuid4())
    return ChannelNodeMappingVariable.construct(rowKey=row_key, variableName=var_name, typeId=type_id, dictId=dict_id,
                                                isArray=is_array, isComplex=is_complex,
                                                isDict=is_dict, isLiteral=is_literal,
                                                variablePath=variable_path, variableRootId=variable_root_id,
                                                nodeVariable=node_variable, externalId=var_id,
                                                id=param_id,
                                                isVariableFromTemplate=is_variable_from_channel_template,
                                                mandatoryFlag=mandatory_flag)


def comms_node_construct(chanel_name, chanel_id, chanel_vers_id,
                         comms_vars=None, node_var_mapps=None, output_var_mapps=None):
    if node_var_mapps is None:
        node_var_mapps = []
    return Communication.construct(communicationChannelName=chanel_name,
                                   channelId=chanel_id,
                                   channelVersionId=chanel_vers_id,
                                   communicationFields=comms_vars,
                                   nodeVariablesMapping=node_var_mapps,
                                   outputVariablesMapping=output_var_mapps)


def empty_node_construct(x, y, node_type: IntNodeType, diagram_version_id, node_name=None,
                         properties=None):
    position = NodeMetaInfo(position=Position(x=x, y=y))

    node = NodeCreateDto.construct(nodeTypeId=node_type,
                                   diagramVersionId=diagram_version_id,
                                   nodeName=node_name,
                                   metaInfo=position,
                                   properties=properties)

    return node


def all_node_construct(x, y, temp_version_id, node_name, int_node_type,
                       properties=None,
                       operation="create", node_name_up=None, descr_up=None,
                       node_id=None, valid_flag=True):
    node = None
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if operation == "create":
        node = NodeCreateDto.construct(nodeTypeId=int_node_type,
                                       diagramVersionId=temp_version_id,
                                       nodeName=node_name,
                                       metaInfo=position,
                                       properties=properties)

    if operation == "update":
        if node_name_up is None:
            node = NodeUpdateDto.construct(nodeId=node_id,
                                           nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name,
                                           nodeDescription=None,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)
        else:
            node = NodeUpdateDto.construct(nodeId=node_id,
                                           nodeTypeId=int_node_type,
                                           diagramVersionId=temp_version_id,
                                           nodeName=node_name_up,
                                           nodeDescription=descr_up,
                                           properties=properties,
                                           metaInfo=position,
                                           validFlag=valid_flag)

    return node
