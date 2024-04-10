import pytest

from common.generators import generate_string
from products.Decision.conftest import db_user
from products.Decision.framework.db_framework import db_model
from products.Decision.framework.db_framework.db_steps.db_steps_test_tables import insert_values
from products.Decision.framework.model import NodeViewShortInfo, DiagramViewDto, DiagramInOutParameterFullViewDto, TablesDto, \
    ColumnsDto, ResponseDto, DataProviderGetFullView
from products.Decision.framework.steps.decision_steps_data_provider_api import get_data_provider_tables, \
    get_data_provider_table
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version, put_diagram_submit
from products.Decision.framework.steps.decision_steps_nodes import update_node
from products.Decision.utilities.custom_models import IntValueType, BasicPrimitiveValues
from products.Decision.utilities.node_cunstructors import read_variable, read_array_variable, \
    variables_for_node, node_update_construct, read_properties, read_node_construct


@pytest.fixture()
def read_array_saved(super_user,
                     create_db_all_tables_and_scheme,
                     provider_constructor,
                     diagram_constructor,
                     save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом чтение данных с чтением массива
    """
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    type_version_id = diagram_constructor["complex_type"]
    node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
    provider_info = provider_constructor["provider_info"]
    columns: list[ColumnsDto] = provider_constructor["columns"]
    table_name = provider_constructor["table_name"]
    node_end_id = diagram_constructor["nodes"]["завершение"].nodeId

    int_column = list(filter(lambda column: column.dataType == "integer", columns)).pop()
    float_column = list(filter(lambda column: column.dataType == "double precision", columns)).pop()
    date_column = list(filter(lambda column: column.dataType == "date", columns)).pop()
    string_column = list(filter(lambda column: column.dataType == "character varying", columns)).pop()

    out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
    in_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
    arr_var = read_array_variable(var_name="in_cmplx")
    out_var_1 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="float_attr",
                              type_id=IntValueType.float.value, var_path="in_cmplx",
                              var_root_id=type_version_id.versionId, node_variable=float_column.columnName,
                              is_jdbc_arr_key=False, array_var=arr_var)
    out_var_2 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="date_attr",
                              type_id=IntValueType.date.value, var_path="in_cmplx",
                              var_root_id=type_version_id.versionId, node_variable=date_column.columnName,
                              is_jdbc_arr_key=False, array_var=arr_var)
    out_var_3 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="string_attr",
                              type_id=IntValueType.str.value, var_path="in_cmplx",
                              var_root_id=type_version_id.versionId, node_variable=string_column.columnName,
                              is_jdbc_arr_key=True, array_var=arr_var)
    node_read_properties = read_properties(data_provider_uuid=provider_info.sourceId,
                                           query=f"select {float_column.columnName}, {date_column.columnName}, "
                                                 f"{string_column.columnName}" + " \n" + f"from {table_name}" + " \n" +
                                                 f"where {int_column.columnName} = $" + "{" + f"{in_var.parameterName}" + "}",
                                           allow_multi_result_response=True,
                                           out_mapping_vars=[out_var_1, out_var_2, out_var_3],
                                           selected_table_names=["table_for_read_array"])
    update_body = read_node_construct(x=700, y=202.22915649414062,
                                      temp_version_id=temp_version_id,
                                      properties=node_read_properties,
                                      operation="update")
    update_node(super_user, node_id=node_read.nodeId, body=update_body)
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
    new_diagram_name = "ag_test_diagram_read_arr" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def diagram_read_2(super_user, diagram_constructor, provider_constructor, create_db_all_tables_and_scheme):
    diagram_id = diagram_constructor["diagram_id"]
    temp_version_id = diagram_constructor["temp_version_id"]
    node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
    node_read_id = node_read.nodeId
    node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    finish_node_id = node_end.nodeId
    provider_info = provider_constructor["provider_info"]
    columns = provider_constructor["columns"]
    table_name = provider_constructor["table_name"]
    db_table = create_db_all_tables_and_scheme[table_name]
    source_id = provider_info.sourceId
    env_id = provider_constructor["env_id"]
    diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
    table_name = provider_constructor["table_name"]
    table_columns = provider_constructor["columns"]
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

    yield {"node_end": node_end, "node_read": node_read,
           "param": diagram_param, "temp_version_id": temp_version_id,
           "table_columns": table_columns, "diagram_id": diagram_id,
           "data_provider": provider_info, "table_name": table_name, "env_id": env_id, "source_id": source_id,
           "db_table": db_table}


@pytest.fixture()
def diagram_read_submit_2(super_user,
                          diagram_read_2,
                          save_diagrams_gen):
    source_id = diagram_read_2["source_id"]
    env_id = diagram_read_2["env_id"]
    node_read = diagram_read_2["node_read"]
    diagram_param = diagram_read_2["param"]
    temp_version_id = diagram_read_2["temp_version_id"]
    diagram_id = diagram_read_2["diagram_id"]
    columns: list[ColumnsDto] = diagram_read_2["table_columns"]
    # tables: list[TablesDto] = diagram_read_2["tables"]
    provider: DataProviderGetFullView = diagram_read_2["data_provider"]
    table_name = diagram_read_2["table_name"]
    column_name = list(filter(lambda column: column.dataType == "integer", columns)).pop().columnName

    output_var_mapping = read_variable(is_arr=False,
                                       is_compl=False,
                                       is_dict=False,
                                       var_name=diagram_param.parameterName,
                                       type_id="1",
                                       node_variable=column_name,
                                       is_jdbc_arr_key=False,
                                       param_id=diagram_param.parameterId)
    node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                           query=f"select {column_name}" + " \n" + f"from {table_name}",
                                           allow_multi_result_response=False,
                                           out_mapping_vars=[output_var_mapping],
                                           selected_table_names=[table_name],
                                           plain_query=f"select {column_name} from {table_name}")
    update_body = read_node_construct(x=700, y=202.22915649414062,
                                      temp_version_id=temp_version_id,
                                      properties=node_read_properties,
                                      operation="update")
    update_node(super_user, node_id=node_read.nodeId, body=update_body)

    diagram_name = "ag_diagram_read" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    # response_save: ResponseDto = ResponseDto.construct(
    #     **save_diagrams_gen.save_diagram(diagram_id=diagram_id,
    #                                      temp_version_id=temp_version_id,
    #                                      new_diagram_name=diagram_name,
    #                                      diagram_description=diagram_description).body)
    #
    # saved_version_id = response_save.uuid
    submit_response = put_diagram_submit(super_user, diagram_id)
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    return {"deploy_id": deploy_id, "env_id": env_id, "diagram_param": diagram_param,
            "diagram_id": diagram_id, "diagram_name": diagram_name,
            "saved_version_id": saved_version_id, "source_id": source_id}
