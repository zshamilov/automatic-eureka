from products.Decision.framework.model import TarantoolWrite, NodeMetaInfo, Position, NodeUpdateDto, TarantoolRead


def tarantool_insert_construct(diagram_vers_id, source_id, table_name,
                               query_type, selected_index_name: str = None,
                               node_name="Tarantool запись", x=600, y=200,
                               schema_name=None,
                               array_flag: bool = False,
                               input_vars_update_mapping=None, input_vars_cond_mapping=None,
                               filter_vars=None, valid_flag=True):
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if input_vars_cond_mapping is None:
        input_vars_cond_mapping = []
    if filter_vars is None:
        filter_vars = []
    if input_vars_update_mapping is None:
        input_vars_update_mapping = []
    properties = TarantoolWrite.construct(dataProviderUuid=source_id,
                                          tableName=table_name,
                                          schemaName=schema_name,
                                          queryType=query_type,
                                          arrayFlag=array_flag,
                                          inputVariablesUpdateMapping=input_vars_update_mapping,
                                          inputVariablesConditionMapping=input_vars_cond_mapping,
                                          filterVariables=filter_vars,
                                          selectedIndexName=selected_index_name)
    node = NodeUpdateDto.construct(nodeTypeId=21,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node


def tarantool_read_construct(diagram_vers_id, source_id, selected_table_names, search_type,
                             allow_multi_result_response: bool = False,
                             node_name="Tarantool чтение", x=400, y=200, input_vars_mapping=None,
                             output_vars_mapping=None, index_vars_mapping=None, query=None, data_provider_name=None,
                             selected_searcher_name=None,
                             lua_result_type=None, plain_query=None, valid_flag=True):
    position = NodeMetaInfo(position=Position(x=x, y=y))
    if input_vars_mapping is None:
        input_vars_mapping = []
    if output_vars_mapping is None:
        output_vars_mapping = []
    if index_vars_mapping is None:
        index_vars_mapping = []
    properties = TarantoolRead.construct(selectedTableNames=selected_table_names,
                                         dataProviderUuid=source_id,
                                         allowMultiResultResponse=allow_multi_result_response,
                                         query=query,
                                         outputVariablesMapping=output_vars_mapping,
                                         searchType=search_type,
                                         dataProviderName=data_provider_name,
                                         selectedSearcherName=selected_searcher_name,
                                         inputVariablesMapping=input_vars_mapping,
                                         readByIndexInputMappingVariables=index_vars_mapping,
                                         luaResultType=lua_result_type,
                                         plainQuery=plain_query
                                         )
    node = NodeUpdateDto.construct(nodeTypeId=20,
                                   diagramVersionId=diagram_vers_id,
                                   nodeName=node_name,
                                   nodeDescription=None,
                                   properties=properties,
                                   metaInfo=position,
                                   validFlag=valid_flag)
    return node
