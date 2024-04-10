import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, NodeValidateDto, NodeViewWithVariablesDto, \
    DiagramViewDto, ColumnsDto, DiagramInOutParameterFullViewDto, QueryType1
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.utilities.custom_models import IntValueType
from products.Decision.utilities.node_cunstructors import insert_input_var_mapping
from products.Decision.utilities.tarantool_node_constructos import tarantool_insert_construct


@pytest.fixture()
def tarantool_insert_update_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
    in_v1: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_1"]
    in_v2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_2"]
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    searched_index = provider_constructor["index"]
    columnns_for_cond = []
    columnns_for_upd = []
    for column in columns:
        if column.isPrimary:
            if column.dataType == "long":
                columnns_for_cond.append(column)
        else:
            if column.dataType == "long":
                columnns_for_upd.append(column)
    cond_var_1 = insert_input_var_mapping(var_name=in_out_v.parameterName, type_id=IntValueType.long.value,
                                          providers_column_name=columnns_for_cond[0].columnName,
                                          providers_column_data_type=columnns_for_cond[0].dataType,
                                          param_id=in_out_v.parameterId)
    cond_var_2 = insert_input_var_mapping(var_name=in_v1.parameterName, type_id=IntValueType.long.value,
                                          providers_column_name=columnns_for_cond[1].columnName,
                                          providers_column_data_type=columnns_for_cond[1].dataType,
                                          param_id=in_v1.parameterId)
    update_var = insert_input_var_mapping(var_name=in_v2.parameterName, type_id=IntValueType.long.value,
                                          providers_column_name=columnns_for_upd[0].columnName,
                                          providers_column_data_type=columnns_for_upd[0].dataType,
                                          param_id=in_v2.parameterId)
    tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                source_id=provider_info.sourceId, table_name="CONTACT",
                                                selected_index_name=searched_index.indexName,
                                                query_type=QueryType1.UPDATE,
                                                input_vars_update_mapping=[update_var],
                                                input_vars_cond_mapping=[cond_var_1, cond_var_2])
    update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)

    new_diagram_name = "ag_test_diagram_tarantool_insert_update" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data, "provider_info": provider_info}


@pytest.fixture()
def tarantool_insert_insert_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
    in_v1: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_1"]
    in_v2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_2"]
    in_str_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_str"]
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    columnns_long = []
    columnns_str = []
    for column in columns:
        if column.dataType == "long":
            columnns_long.append(column)
        if column.dataType == "string":
            columnns_str.append(column)
    update_var_1 = insert_input_var_mapping(var_name="in_out_int", type_id=IntValueType.long.value,
                                            providers_column_name=columnns_long[0].columnName,
                                            providers_column_data_type=columnns_long[0].dataType,
                                            param_id=in_out_v.parameterId)
    update_var_2 = insert_input_var_mapping(var_name="in_int_1", type_id=IntValueType.long.value,
                                            providers_column_name=columnns_long[1].columnName,
                                            providers_column_data_type=columnns_long[1].dataType,
                                            param_id=in_v1.parameterId)
    update_var_3 = insert_input_var_mapping(var_name="in_int_2", type_id=IntValueType.long.value,
                                            providers_column_name=columnns_long[2].columnName,
                                            providers_column_data_type=columnns_long[2].dataType,
                                            param_id=in_v2.parameterId)
    update_var_4 = insert_input_var_mapping(var_name="in_str", type_id=IntValueType.str.value,
                                            providers_column_name=columnns_str[0].columnName,
                                            providers_column_data_type=columnns_str[0].dataType,
                                            param_id=in_str_v.parameterId)
    tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                source_id=provider_info.sourceId, table_name="CONTACT",
                                                query_type=QueryType1.INSERT,
                                                input_vars_update_mapping=[update_var_1, update_var_2,
                                                                           update_var_3, update_var_4])
    update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)

    new_diagram_name = "ag_test_diagram_tarantool_insert_insert" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def tarantool_insert_upsert_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
    in_v1: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_1"]
    in_v2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_2"]
    in_str_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_str"]
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    searched_index = provider_constructor["index"]
    columnns_for_cond = []
    columnn_for_upd_long: ColumnsDto = ColumnsDto.construct()
    columnn_for_upd_str: ColumnsDto = ColumnsDto.construct()
    for column in columns:
        if column.isPrimary:
            if column.dataType == "long":
                columnns_for_cond.append(column)
        else:
            if column.dataType == "long":
                columnn_for_upd_long = column
            if column.dataType == "string":
                columnn_for_upd_str = column
    cond_var_1 = insert_input_var_mapping(var_name="in_out_int", type_id=IntValueType.long.value,
                                          providers_column_name=columnns_for_cond[0].columnName,
                                          providers_column_data_type=columnns_for_cond[0].dataType,
                                          param_id=in_out_v.parameterId)
    cond_var_2 = insert_input_var_mapping(var_name="in_int_1", type_id=IntValueType.long.value,
                                          providers_column_name=columnns_for_cond[1].columnName,
                                          providers_column_data_type=columnns_for_cond[1].dataType,
                                          param_id=in_v1.parameterId)
    update_var_1 = insert_input_var_mapping(var_name="in_int_2", type_id=IntValueType.long.value,
                                            providers_column_name=columnn_for_upd_long.columnName,
                                            providers_column_data_type=columnn_for_upd_long.dataType,
                                            param_id=in_v2.parameterId)
    update_var_2 = insert_input_var_mapping(var_name="in_str", type_id=IntValueType.str.value,
                                            providers_column_name=columnn_for_upd_str.columnName,
                                            providers_column_data_type=columnn_for_upd_str.dataType,
                                            param_id=in_str_v.parameterId)
    tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                source_id=provider_info.sourceId, table_name="CONTACT",
                                                selected_index_name=searched_index.indexName,
                                                query_type=QueryType1.MERGE,
                                                input_vars_update_mapping=[update_var_1, update_var_2],
                                                input_vars_cond_mapping=[cond_var_1, cond_var_2])
    update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)

    new_diagram_name = "ag_test_diagram_tarantool_insert_upsert" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def tarantool_constant_insert_update_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    searched_index = provider_constructor["index"]
    columnns_for_cond = []
    columnns_for_upd = []
    for column in columns:
        if column.isPrimary:
            if column.dataType == "long":
                columnns_for_cond.append(column)
        else:
            if column.dataType == "long":
                columnns_for_upd.append(column)
    cond_var_1 = insert_input_var_mapping(var_name=5, type_id="2",
                                          providers_column_name=columnns_for_cond[0].columnName,
                                          providers_column_data_type=columnns_for_cond[0].dataType,
                                          is_literal=True)
    cond_var_2 = insert_input_var_mapping(var_name=4, type_id="2",
                                          providers_column_name=columnns_for_cond[1].columnName,
                                          providers_column_data_type=columnns_for_cond[1].dataType,
                                          is_literal=True)
    update_var = insert_input_var_mapping(var_name=777, type_id="2",
                                          providers_column_name=columnns_for_upd[0].columnName,
                                          providers_column_data_type=columnns_for_upd[0].dataType,
                                          is_literal=True)
    tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                source_id=provider_info.sourceId, table_name="CONTACT",
                                                selected_index_name=searched_index.indexName,
                                                query_type=QueryType1.UPDATE,
                                                input_vars_update_mapping=[update_var],
                                                input_vars_cond_mapping=[cond_var_1, cond_var_2])
    update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))

    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
    new_diagram_name = "ag_test_diagram_tarantool_insert_insert" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def tarantool_constant_insert_insert_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    columns_long = []
    columns_str = []
    columns_float = []
    columns_int = []
    columns_bool = []
    columns_dateTime = []
    columns_time = []
    columns_date = []
    columns_double = []
    for column in columns:
        if column.dataType == "long":
            columns_long.append(column)
        if column.dataType == "string":
            columns_str.append(column)
        if column.dataType == "float":
            columns_float.append(column)
        if column.dataType == "int":
            columns_int.append(column)
        if column.dataType == "boolean":
            columns_bool.append(column)
        if column.dataType == "DateTime":
            columns_dateTime.append(column)
        if column.dataType == "Time":
            columns_time.append(column)
        if column.dataType == "Date":
            columns_date.append(column)
        if column.dataType == "double":
            columns_double.append(column)

    update_var_1 = insert_input_var_mapping(var_name=12345, type_id="2",
                                            providers_column_name=columns_long[0].columnName,
                                            providers_column_data_type=columns_long[0].dataType,
                                            is_literal=True)
    update_var_2 = insert_input_var_mapping(var_name="'line'", type_id="2",
                                            providers_column_name=columns_str[0].columnName,
                                            providers_column_data_type=columns_str[0].dataType,
                                            is_literal=True)
    update_var_3 = insert_input_var_mapping(var_name="'line2'", type_id="2",
                                            providers_column_name=columns_str[1].columnName,
                                            providers_column_data_type=columns_str[1].dataType,
                                            is_literal=True)
    update_var_4 = insert_input_var_mapping(var_name=9.0, type_id="2",
                                            providers_column_name=columns_float[0].columnName,
                                            providers_column_data_type=columns_float[0].dataType,
                                            is_literal=True)
    update_var_5 = insert_input_var_mapping(var_name=9.1, type_id="2",
                                            providers_column_name=columns_double[0].columnName,
                                            providers_column_data_type=columns_double[0].dataType,
                                            is_literal=True)
    update_var_6 = insert_input_var_mapping(var_name=1, type_id="2",
                                            providers_column_name=columns_int[0].columnName,
                                            providers_column_data_type=columns_int[0].dataType,
                                            is_literal=True)
    update_var_7 = insert_input_var_mapping(var_name="'true'", type_id="2",
                                            providers_column_name=columns_bool[0].columnName,
                                            providers_column_data_type=columns_bool[0].dataType,
                                            is_literal=True)
    update_var_8 = insert_input_var_mapping(var_name="'2023-12-22 01:01:01.434'", type_id="2",
                                            providers_column_name=columns_dateTime[0].columnName,
                                            providers_column_data_type=columns_dateTime[0].dataType,
                                            is_literal=True)
    update_var_9 = insert_input_var_mapping(var_name="'01:01:01'", type_id="2",
                                            providers_column_name=columns_time[0].columnName,
                                            providers_column_data_type=columns_time[0].dataType,
                                            is_literal=True)
    update_var_10 = insert_input_var_mapping(var_name="'2023-12-22'", type_id="2",
                                             providers_column_name=columns_date[0].columnName,
                                             providers_column_data_type=columns_date[0].dataType,
                                             is_literal=True)
    tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                source_id=provider_info.sourceId,
                                                table_name="TEST_PRIMITIVE_ALL_TYPES",
                                                query_type=QueryType1.INSERT,
                                                input_vars_update_mapping=[update_var_1, update_var_2,
                                                                           update_var_3, update_var_4,
                                                                           update_var_5, update_var_6,
                                                                           update_var_7, update_var_8,
                                                                           update_var_9, update_var_10])
    update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
    new_diagram_name = "ag_test_diagram_tarantool_insert_insert" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def tarantool_constant_insert_upsert_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen):
    in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    searched_index = provider_constructor["index"]
    searched_index = provider_constructor["index"]
    columnns_for_cond = []
    columnn_for_upd_long: ColumnsDto = ColumnsDto.construct()
    columnn_for_upd_str: ColumnsDto = ColumnsDto.construct()
    for column in columns:
        if column.isPrimary:
            if column.dataType == "long":
                columnns_for_cond.append(column)
        else:
            if column.dataType == "long":
                columnn_for_upd_long = column
            if column.dataType == "string":
                columnn_for_upd_str = column
    cond_var_1 = insert_input_var_mapping(var_name=5, type_id="2",
                                          providers_column_name=columnns_for_cond[0].columnName,
                                          providers_column_data_type=columnns_for_cond[0].dataType,
                                          is_literal=True)
    cond_var_2 = insert_input_var_mapping(var_name=4, type_id="2",
                                          providers_column_name=columnns_for_cond[1].columnName,
                                          providers_column_data_type=columnns_for_cond[1].dataType,
                                          is_literal=True)
    update_var_1 = insert_input_var_mapping(var_name=888, type_id="2",
                                            providers_column_name=columnn_for_upd_long.columnName,
                                            providers_column_data_type=columnn_for_upd_long.dataType,
                                            is_literal=True)
    update_var_2 = insert_input_var_mapping(var_name="'str'", type_id="2",
                                            providers_column_name=columnn_for_upd_str.columnName,
                                            providers_column_data_type=columnn_for_upd_str.dataType,
                                            is_literal=True)
    tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                source_id=provider_info.sourceId, table_name="CONTACT",
                                                selected_index_name=searched_index.indexName,
                                                query_type=QueryType1.MERGE,
                                                input_vars_update_mapping=[update_var_1, update_var_2],
                                                input_vars_cond_mapping=[cond_var_1, cond_var_2])
    update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=tarantool_node.nodeTypeId,
                    properties=tarantool_node.properties))
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)

    new_diagram_name = "ag_test_diagram_tarantool_insert_upsert" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}
