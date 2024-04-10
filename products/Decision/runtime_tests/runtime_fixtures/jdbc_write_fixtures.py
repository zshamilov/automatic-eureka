import pytest
from typing import List

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, DiagramViewDto, DiagramInOutParameterFullViewDto, \
    QueryType1, \
    DataProviderGetFullView, NodeViewWithVariablesDto, AttributeGetFullView
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type_attributes
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version, delete_diagram, \
    put_diagram_submit
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.utilities.custom_models import IntValueType, PrimitiveToDatabaseTypeMappings
from products.Decision.utilities.node_cunstructors import read_variable, read_array_variable, \
    variables_for_node, node_update_construct, read_properties, read_node_construct, insert_input_var_mapping, \
    insert_node_properties, insert_node_construct
import products.Decision.framework.db_framework.db_model as model
from products.Decision.utilities.variable_constructors import primitive_value_message_contsructor


@pytest.fixture()
def insert_primitive_array_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen, request):
    """
    Фикстура для создания диаграммы с настроенным узлом сохранение данных с записью примитивного массива
    """
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_write: NodeViewShortInfo = diagram_constructor["nodes"]["запись"]
    provider_info = provider_constructor["provider_info"]
    node_end_id = diagram_constructor["nodes"]["завершение"].nodeId
    in_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
    array_flag_marker = request.node.get_closest_marker("array_flag")
    if array_flag_marker is not None:
        array_flag_var = array_flag_marker.args[0]
    else:
        array_flag_var = False

    table_name = provider_constructor["table_name"]
    columns = provider_constructor["columns"]

    int_column = list(filter(lambda column: column.dataType == "integer", columns)).pop().columnName

    insert_var_update = insert_input_var_mapping(var_name=in_var.parameterName,
                                                 is_arr=True,
                                                 type_id="1",
                                                 providers_column_name=int_column,
                                                 providers_column_data_type="integer",
                                                 param_id=in_var.parameterId)
    insert_properties = insert_node_properties(source_id=provider_info.sourceId,
                                               table_name=table_name,
                                               query_type=QueryType1.INSERT,
                                               input_vars_update_mapping=[insert_var_update],
                                               array_flag=array_flag_var)
    update_body = insert_node_construct(x=700, y=202.22915649414062,
                                        temp_version_id=temp_version_id,
                                        properties=insert_properties,
                                        operation="update")
    update_node(super_user, node_id=node_write.nodeId, body=update_body)

    finish_var = variables_for_node(node_type="finish_out", is_arr=in_var.arrayFlag, is_compl=in_var.complexFlag,
                                    name=in_var.parameterName,
                                    param_name=in_var.parameterName,
                                    type_id=in_var.typeId,
                                    vers_id=in_var.parameterVersionId)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_var])
    update_node(super_user, node_id=node_end_id, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_write_arr" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data, "int_column": int_column,
            "table_name": table_name}


@pytest.fixture()
def diagram_insert_2(super_user, diagram_constructor, provider_constructor, create_db_all_tables_and_scheme):
    table_name = provider_constructor["table_name"]
    columns = provider_constructor["columns"]
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_insert: NodeViewShortInfo = diagram_constructor["nodes"]["запись"]
    insert_node_id = node_insert.nodeId
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    finish_node_id = node_end.nodeId
    provider_info = provider_constructor["provider_info"]
    env_id = provider_constructor["env_id"]
    diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
    diagram_variables = diagram_constructor["variables"]
    schema_name = provider_constructor["schema_name"]
    db_table = create_db_all_tables_and_scheme[table_name]

    finish_variables = variables_for_node(node_type="finish_out",
                                          is_arr=False, is_compl=False,
                                          name="1", type_id=1,
                                          vers_id=diagram_param.parameterId,
                                          param_name=diagram_param.parameterName)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(
        super_user, node_id=node_end.nodeId, body=finish_up_body
    )

    yield {"temp_version_id": temp_version_id, "provider": provider_info,
           "diagram_param": diagram_param, "insert_node_id": insert_node_id,
           "finish_node_id": finish_node_id, "diagram_variables": diagram_variables,
           "env_id": env_id, "diagram_id": diagram_id, "table_name": table_name,
           "columns": columns, "schema_name": schema_name, "db_table": db_table}


@pytest.fixture()
def diagram_insert_saved_2(super_user, diagram_insert_2, save_diagrams_gen):
    table_name = diagram_insert_2["table_name"]
    columns = diagram_insert_2["columns"]
    temp_version_id = diagram_insert_2["temp_version_id"]
    provider: DataProviderGetFullView = diagram_insert_2["provider"]
    insert_node_id = diagram_insert_2["insert_node_id"]
    diagram_param = diagram_insert_2["diagram_param"]
    diagram_id = diagram_insert_2["diagram_id"]
    env_id = diagram_insert_2["env_id"]

    int_column = list(filter(lambda column: column.dataType == "integer", columns)).pop().columnName

    insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                 is_arr=False, is_compl=False,
                                                 type_id="1",
                                                 providers_column_name=int_column,
                                                 providers_column_data_type="integer",
                                                 is_dict=False,
                                                 simple_name_val=diagram_param.parameterName,
                                                 full_path_val=diagram_param.parameterName,
                                                 param_id=diagram_param.parameterId)
    insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                               table_name=table_name,
                                               query_type=QueryType1.INSERT,
                                               input_vars_update_mapping=[insert_var_update])
    update_body = insert_node_construct(x=700, y=202.22915649414062,
                                        temp_version_id=temp_version_id,
                                        properties=insert_properties,
                                        operation="update")
    update_node(super_user, node_id=insert_node_id, body=update_body)

    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, insert_node_id).body
    )

    diagram_name = "ag_diagram_insert" + "_" + generate_string()
    diagram_description = 'diagram created in test'

    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    yield {"diagram_param": diagram_param, "env_id": env_id, "diagram_name": diagram_name,
           "diagram_id": diagram_id, "saved_version_id": saved_version_id, "int_column": int_column,
           "table_name": table_name}

    delete_diagram(super_user, saved_version_id)


@pytest.fixture()
def diagram_insert_submitted_2(super_user, diagram_insert_saved_2):
    diagram_id = diagram_insert_saved_2["diagram_id"]
    diagram_param: DiagramInOutParameterFullViewDto = diagram_insert_saved_2["diagram_param"]
    env_id = diagram_insert_saved_2["env_id"]
    diagram_name = diagram_insert_saved_2["diagram_name"]
    put_diagram_submit(super_user, diagram_id)
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)

    int_column = diagram_insert_saved_2["int_column"]
    table_name = diagram_insert_saved_2["table_name"]

    return {"diagram_param": diagram_param, "env_id": env_id, "diagram_name": diagram_name,
            "diagram_id": diagram_id, "deploy_id": deploy_id, "int_column": int_column,
            "table_name": table_name}


@pytest.fixture()
def insert_ctype_array_saved(super_user, provider_constructor, diagram_constructor, save_diagrams_gen,
                             create_db_all_tables_and_scheme, request):
    """
    Фикстура для создания диаграммы с настроенным узлом сохранение данных с записью примитивного массива
    """
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_write: NodeViewShortInfo = diagram_constructor["nodes"]["запись"]
    provider_info = provider_constructor["provider_info"]
    node_end_id = diagram_constructor["nodes"]["завершение"].nodeId
    in_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_ctype"]
    array_flag_marker = request.node.get_closest_marker("array_flag")
    if array_flag_marker is not None:
        array_flag_var = array_flag_marker.args[0]
    else:
        array_flag_var = False

    in_var_attrs: List[AttributeGetFullView] = [AttributeGetFullView.construct(**attr)
                    for attr in get_custom_type_attributes(super_user, in_var.typeId).body]

    table_name = provider_constructor["table_name"]
    provider_columns = provider_constructor["columns"]

    # так как типы в интерфейсе отличаются от типов в sqlAlchemy - получаем также список колонок Alchemy
    # (чтобы смаппить по типу)
    db_table_columns = create_db_all_tables_and_scheme[table_name].columns
    mapped_ctype_attr_to_db_column = dict()
    ins_node_mappings = []

    # обходим все атрибуты комплексного типа и для каждого маппим колонку таблицы из БД
    for cur_attr in in_var_attrs:
        # получаем тип алхимии для типа переменной текущего атрибута из нашего словаря
        db_datatype = PrimitiveToDatabaseTypeMappings.primitive_to_pg[cur_attr.primitiveTypeId]
        # по типу алхимии берём подходящую колонку БД
        cur_attr_db_column_name = list(
            filter(lambda column: type(column.type) is type(db_datatype), db_table_columns)).pop().name
        # добавляем в список маппингов
        mapped_ctype_attr_to_db_column[cur_attr.attributeName] = cur_attr_db_column_name
        # по имени подходящей колонки в БД берём тип в интерфейсе
        cur_column_provider_type = list(
            filter(lambda column: column.columnName == cur_attr_db_column_name, provider_columns)).pop().dataType
        # заполняем маппинг для переменной узла
        cur_mapping = insert_input_var_mapping(var_name=cur_attr.attributeName,
                                               var_path=in_var.parameterName,
                                               is_arr=False,
                                               type_id=cur_attr.primitiveTypeId,
                                               providers_column_name=cur_attr_db_column_name,
                                               providers_column_data_type=cur_column_provider_type,
                                               var_root_id=in_var.typeId,
                                               array_var_name=in_var.parameterName,
                                               array_var_path="")
        ins_node_mappings.append(cur_mapping)

    insert_properties = insert_node_properties(source_id=provider_info.sourceId,
                                               table_name=table_name,
                                               query_type=QueryType1.INSERT,
                                               input_vars_update_mapping=ins_node_mappings,
                                               array_flag=array_flag_var)
    update_body = insert_node_construct(x=700, y=202.22915649414062,
                                        temp_version_id=temp_version_id,
                                        properties=insert_properties,
                                        operation="update")
    update_node(super_user, node_id=node_write.nodeId, body=update_body)

    finish_var = variables_for_node(node_type="finish_out", is_arr=in_var.arrayFlag, is_compl=in_var.complexFlag,
                                    name=in_var.parameterName,
                                    param_name=in_var.parameterName,
                                    type_id=in_var.typeId,
                                    vers_id=in_var.parameterVersionId)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_var])
    update_node(super_user, node_id=node_end_id, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_write_arr_ctype" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data,
            "mapped_ctype_attr_to_db_column": mapped_ctype_attr_to_db_column,
            "table_name": table_name, "in_var_attrs": in_var_attrs}
