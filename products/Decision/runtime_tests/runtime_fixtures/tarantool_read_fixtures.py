import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, SearchType, NodeValidateDto, NodeViewWithVariablesDto, \
    DiagramViewDto, FunctionsDto, LuaResultType, IndexDto, DiagramInOutParameterFullViewDto, Predicate
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.utilities.custom_models import IntValueType
from products.Decision.utilities.node_cunstructors import tarantool_read_input_var, read_variable, read_array_variable, \
    variables_for_node, node_update_construct, tarantool_read_index_var
from products.Decision.utilities.tarantool_node_constructos import tarantool_read_construct


@pytest.fixture()
def tarantool_read_index_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом чтение Tarantool с типом блока поиск по индексу
    """
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    indexes = provider_constructor["index"]
    node_end_id = diagram_constructor["nodes"]["завершение"].nodeId
    out_var_long: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_long"]
    out_var_str: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_str"]
    in_long1_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_long_1"]
    in_long2_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_long_2"]
    columns_for_inp = []
    columns_for_read = []
    index: IndexDto
    for column in columns:
        if column.isPrimary:
            columns_for_inp.append(column)
        else:
            columns_for_read.append(column)
    for indx in indexes:
        if indx.isUnique:
            index = indx
    inp_var_1 = tarantool_read_input_var(var_name=in_long1_v.parameterName, type_id=IntValueType.long.value,
                                         providers_column_name=columns_for_inp[0].columnName,
                                         providers_column_data_type=columns_for_inp[0].dataType,
                                         param_id=in_long1_v.parameterId)
    inp_var_2 = tarantool_read_input_var(var_name=in_long2_v.parameterName, type_id=IntValueType.long.value,
                                         providers_column_name=columns_for_inp[1].columnName,
                                         providers_column_data_type=columns_for_inp[1].dataType,
                                         param_id=in_long2_v.parameterId)
    index_var = tarantool_read_index_var(index_name=index.indexName,
                                         predicate=Predicate.EQUALS,
                                         order=0,
                                         input_vars_mapping=[inp_var_1, inp_var_2])
    read_var_1 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name=out_var_long.parameterName,
                               type_id=IntValueType.long.value, node_variable=columns_for_read[0].columnName,
                               is_jdbc_arr_key=False, node_variable_type=columns_for_read[0].dataType,
                               param_id=out_var_long.parameterId)
    read_var_2 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name=out_var_str.parameterName,
                               type_id=IntValueType.str.value, node_variable=columns_for_read[1].columnName,
                               is_jdbc_arr_key=False, node_variable_type=columns_for_read[1].dataType,
                               param_id=out_var_str.parameterId)
    tarantool_node = tarantool_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                              source_id=provider_info.sourceId,
                                              selected_table_names=["CONTACT"],
                                              search_type=SearchType.INDEX_SEARCH,
                                              index_vars_mapping=[index_var],
                                              output_vars_mapping=[read_var_1, read_var_2],
                                              data_provider_name=provider_info.sourceName,
                                              selected_searcher_name="")
    update_node(super_user, node_id=node_tarantool_read.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_read.nodeId).body)
    finish_var_l = variables_for_node(node_type="finish_out", is_arr=out_var_long.arrayFlag,
                                      is_compl=out_var_long.complexFlag,
                                      name=out_var_long.parameterName,
                                      param_name=out_var_long.parameterName,
                                      type_id=out_var_long.typeId,
                                      vers_id=out_var_long.parameterVersionId)
    finish_var_s = variables_for_node(node_type="finish_out", is_arr=out_var_str.arrayFlag,
                                      is_compl=out_var_str.complexFlag,
                                      name=out_var_str.parameterName,
                                      param_name=out_var_str.parameterName,
                                      type_id=out_var_str.typeId,
                                      vers_id=out_var_str.parameterVersionId)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_var_s, finish_var_l])
    update_node(super_user, node_id=node_end_id, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_tarantool_read_index" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def tarantool_read_function_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом чтение Tarantool с типом блока вызов функции
    Выбранная функция возвращает сумму двух аргументов, результат работы функции - константа
    """
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение тарантул"]
    provider_info = provider_constructor["provider_info"]
    functions = provider_constructor["functions"]
    node_end_id = diagram_constructor["nodes"]["завершение"].nodeId
    out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int"]
    input_params = []
    function: FunctionsDto
    for func in functions:
        if func.name == "get_sum":
            function = func
    for func in function.arguments:
        input_params.append(func)
    inp_var_1 = tarantool_read_input_var(var_name="in_int_1", type_id=IntValueType.int.value,
                                         providers_column_name=input_params[0],
                                         providers_column_data_type=None, is_null=False)
    inp_var_2 = tarantool_read_input_var(var_name="in_int_2", type_id=IntValueType.int.value,
                                         providers_column_name=input_params[1],
                                         providers_column_data_type=None, is_null=False)
    calc_var = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="out_int",
                             type_id=IntValueType.int.value, is_jdbc_arr_key=True)
    tarantool_node = tarantool_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                              source_id=provider_info.sourceId,
                                              selected_table_names=None,
                                              search_type=SearchType.LUA_FUNCTION_SEARCH,
                                              input_vars_mapping=[inp_var_1, inp_var_2],
                                              output_vars_mapping=[calc_var],
                                              query=function.body,
                                              data_provider_name=provider_info.sourceName,
                                              selected_searcher_name=function.name,
                                              lua_result_type=LuaResultType.SCALAR,
                                              plain_query=function.body)
    update_node(super_user, node_id=node_tarantool_read.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_read.nodeId).body)
    finish_var = variables_for_node(node_type="finish_out", is_arr=out_var.arrayFlag, is_compl=False,
                                    name=out_var.parameterName,
                                    param_name=out_var.parameterName,
                                    type_id=out_var.typeId,
                                    vers_id=out_var.parameterVersionId)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_var])
    update_node(super_user, node_id=node_end_id, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_tarantool_read_func" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def tarantool_read_array_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом чтение Tarantool с типом блока поиск по индексу и чтением массива
    """
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    type_version_id = diagram_constructor["complex_type"]
    node_tarantool_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    indexes = provider_constructor["index"]
    node_end_id = diagram_constructor["nodes"]["завершение"].nodeId
    out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
    columns_for_inp = []
    columns_for_read = []
    index: IndexDto = None
    for indx in indexes:
        if not indx.isUnique:
            index = indx
    indx_clmn = index.columns[0]
    for column in columns:
        if column.columnName == indx_clmn:
            columns_for_inp.append(column)
        else:
            columns_for_read.append(column)
    inp_var_1 = tarantool_read_input_var(var_name="in_long", type_id=IntValueType.long.value,
                                         providers_column_name=columns_for_inp[0].columnName,
                                         providers_column_data_type=columns_for_inp[0].dataType)
    index_var = tarantool_read_index_var(index_name=index.indexName,
                                         predicate=Predicate.EQUALS,
                                         order=0,
                                         input_vars_mapping=[inp_var_1])
    arr_var = read_array_variable(var_name="in_cmplx")
    read_var_1 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="long_attr1",
                               type_id=IntValueType.long.value, var_path="in_cmplx",
                               var_root_id=type_version_id.versionId, node_variable=columns_for_read[0].columnName,
                               is_jdbc_arr_key=True, array_var=arr_var, node_variable_type=columns_for_read[0].dataType)
    read_var_2 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="long_attr2",
                               type_id=IntValueType.long.value, var_path="in_cmplx",
                               var_root_id=type_version_id.versionId, node_variable=columns_for_read[1].columnName,
                               is_jdbc_arr_key=False, array_var=arr_var,
                               node_variable_type=columns_for_read[1].dataType)
    tarantool_node = tarantool_read_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                              source_id=provider_info.sourceId,
                                              selected_table_names=["OfferLower"],
                                              search_type=SearchType.INDEX_SEARCH,
                                              allow_multi_result_response=True,
                                              index_vars_mapping=[index_var],
                                              output_vars_mapping=[read_var_1, read_var_2],
                                              data_provider_name=provider_info.sourceName,
                                              selected_searcher_name="")
    update_node(super_user, node_id=node_tarantool_read.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_read.nodeId).body)
    finish_var = variables_for_node(node_type="finish_out", is_arr=out_var.arrayFlag, is_compl=out_var.complexFlag,
                                    name=out_var.parameterName,
                                    param_name=out_var.parameterName,
                                    type_id=out_var.typeId,
                                    vers_id=out_var.parameterVersionId)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_var])
    update_node(super_user, node_id=node_end_id, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_tarantool_read_arr" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


