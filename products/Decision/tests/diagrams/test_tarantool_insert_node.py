import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, DiagramViewDto, NodeViewShortInfo, QueryType1, \
    NodeValidateDto, NodeViewWithVariablesDto, DiagramInOutParameterFullViewDto, ColumnsDto

from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version

from products.Decision.framework.steps.decision_steps_nodes import create_node, delete_node_by_id, get_node_by_id, \
    update_node
from products.Decision.utilities.custom_models import IntNodeType, VariableParams, IntValueType
from products.Decision.utilities.node_cunstructors import empty_node_construct, insert_input_var_mapping
from products.Decision.utilities.tarantool_node_constructos import tarantool_insert_construct


@allure.epic("Диаграммы")
@allure.feature("Узел записи tarantool")
@pytest.mark.scenario("DEV-8462")
class TestDiagramsTarantoolWriteNode:
    @allure.story("Узел вставки tarantool создаётся")
    @allure.title(
        "Создать диаграмму с узлом записи tarantool без параметров, увидеть, что создался"
    )
    @pytest.mark.smoke
    def test_create_tarantool_write_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла вставки tarantool"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.tarantoolWrite,
                                             diagram_version_id=temp_version_id,
                                             node_name="Запись Tarantool")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла корректен и равен запись tarantool"
        ):
            assert diagram.nodes[str(node_id)].nodeTypeId == IntNodeType.tarantoolWrite

    @allure.story("Узел чтения удаляется")
    @allure.title(
        "Создать диаграмму с узлом вставки-tarantool без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.smoke
    def test_delete_node_tarantool_write(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла вставки tarantool"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.tarantoolWrite,
                                             diagram_version_id=temp_version_id,
                                             node_name="Запись Tarantool")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_id).status == 404

    @allure.story(
        "В узле чтения возможно добавить источник данных и выбрать поле из таблицы"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_valid(self, super_user, provider_constructor, diagram_constructor):
        in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
        in_v1: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_1"]
        in_v2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_2"]
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
        cond_var_1 = insert_input_var_mapping(var_name="in_out_int", type_id=IntValueType.long.value,
                                              providers_column_name=columnns_for_cond[0].columnName,
                                              providers_column_data_type=columnns_for_cond[0].dataType,
                                              param_id=in_out_v.parameterId)
        cond_var_2 = insert_input_var_mapping(var_name="in_int_1", type_id=IntValueType.long.value,
                                              providers_column_name=columnns_for_cond[1].columnName,
                                              providers_column_data_type=columnns_for_cond[1].dataType,
                                              param_id=in_v1.parameterId)
        update_var = insert_input_var_mapping(var_name="in_int_2", type_id=IntValueType.long.value,
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
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert node_view.validFlag

    @allure.story(
        "Узел Tarantool запись валидный при маппинге на константы для режима 'Вставка данных'"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы в "
        "маппинге использовать константу"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("TEST_PRIMITIVE_TYPES")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_insert_constant_valid(self, super_user, integration_user, provider_constructor,
                                                        diagram_constructor):
        with allure.step("Получение информации"):
            node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
            provider_info = provider_constructor["provider_info"]
            columns = provider_constructor["columns"]
            columns_long = []
            columns_str = []
            columns_float = []
            columns_int = []
            columns_bool = []
            columns_datetime = []
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
                    columns_datetime.append(column)
                if column.dataType == "Time":
                    columns_time.append(column)
                if column.dataType == "Date":
                    columns_date.append(column)
                if column.dataType == "double":
                    columns_double.append(column)

        with allure.step("Обновление узла Запись Тарантул с записью констант в мапинг узла с режимом 'Вставка'"):
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
                                                    providers_column_name=columns_datetime[0].columnName,
                                                    providers_column_data_type=columns_datetime[0].dataType,
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
                                                        table_name="TEST_PRIMITIVE_TYPES",
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
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert node_view.validFlag

    @allure.story(
        "Узел Tarantool запись валидный при незаполненных isNullable = true полях для режима 'Вставка данных'"
        " при маппинге на константы "
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы в "
        "маппинге использовать константу, не запонять поле при isNullable = true"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("TEST_PRIMITIVE_TYPES")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    @allure.issue("DEV-22947")
    def test_tarantool_write_node_insert_constant_nullable(self, super_user, integration_user, provider_constructor,
                                                           diagram_constructor):
        with allure.step("Получение информации о диаграмме и источнике"):
            node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
            provider_info = provider_constructor["provider_info"]
            columns = provider_constructor["columns"]
            columns_null = []
            columns_long = []
            columns_str = []
            columns_float = []
            columns_int = []
            columns_bool = []
            columns_datetime = []
            columns_time = []
            columns_date = []
            columns_double = []
            for column in columns:
                if column.isNullable:
                    if column.dataType == "string":
                        columns_null.append(column)
                else:
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
                        columns_datetime.append(column)
                    if column.dataType == "Time":
                        columns_time.append(column)
                    if column.dataType == "Date":
                        columns_date.append(column)
                    if column.dataType == "double":
                        columns_double.append(column)

        with allure.step("Обновление узла Запись Тарантул с записью констант в мапинг узла,"
                         " не заполнять значение, isNullable = true"):
            update_var_1 = insert_input_var_mapping(var_name=12345, type_id="2",
                                                    providers_column_name=columns_long[0].columnName,
                                                    providers_column_data_type=columns_long[0].dataType,
                                                    is_literal=True)
            update_var_2 = insert_input_var_mapping(var_name="'line'", type_id="2",
                                                    providers_column_name=columns_str[0].columnName,
                                                    providers_column_data_type=columns_str[0].dataType,
                                                    is_literal=True)
            update_var_3 = insert_input_var_mapping(var_name=9.0, type_id="2",
                                                    providers_column_name=columns_float[0].columnName,
                                                    providers_column_data_type=columns_float[0].dataType,
                                                    is_literal=True)
            update_var_4 = insert_input_var_mapping(var_name=9.1, type_id="2",
                                                    providers_column_name=columns_double[0].columnName,
                                                    providers_column_data_type=columns_double[0].dataType,
                                                    is_literal=True)
            update_var_5 = insert_input_var_mapping(var_name=1, type_id="2",
                                                    providers_column_name=columns_int[0].columnName,
                                                    providers_column_data_type=columns_int[0].dataType,
                                                    is_literal=True)
            update_var_6 = insert_input_var_mapping(var_name="'true'", type_id="2",
                                                    providers_column_name=columns_bool[0].columnName,
                                                    providers_column_data_type=columns_bool[0].dataType,
                                                    is_literal=True)
            update_var_7 = insert_input_var_mapping(var_name="'2023-12-22 01:01:01.434'", type_id="2",
                                                    providers_column_name=columns_datetime[0].columnName,
                                                    providers_column_data_type=columns_datetime[0].dataType,
                                                    is_literal=True)
            update_var_8 = insert_input_var_mapping(var_name="'01:01:01'", type_id="2",
                                                    providers_column_name=columns_time[0].columnName,
                                                    providers_column_data_type=columns_time[0].dataType,
                                                    is_literal=True)
            update_var_9 = insert_input_var_mapping(var_name="'2023-12-22'", type_id="2",
                                                    providers_column_name=columns_date[0].columnName,
                                                    providers_column_data_type=columns_date[0].dataType,
                                                    is_literal=True)
            update_var_10 = insert_input_var_mapping(var_name="", type_id="2",
                                                     providers_column_name=columns_null[0].columnName,
                                                     providers_column_data_type=columns_null[0].dataType,
                                                     is_null=True)
            tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                        source_id=provider_info.sourceId,
                                                        table_name="TEST_PRIMITIVE_TYPES",
                                                        query_type=QueryType1.INSERT,
                                                        input_vars_update_mapping=[update_var_1, update_var_2,
                                                                                   update_var_3, update_var_4,
                                                                                   update_var_5,
                                                                                   update_var_6, update_var_7,
                                                                                   update_var_8, update_var_9,
                                                                                   update_var_10])
            update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=tarantool_node.nodeTypeId,
                            properties=tarantool_node.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел, узел валиден"):
            assert node_view.validFlag

    @allure.story(
        "Узел Tarantool запись валидный при маппинге полей индекса на константы для режима 'Обновление данных'"
    )
    @allure.title(
        "Обновить узел записи добавив к нему валидный источник данных и указать поле из таблицы в "
        "маппинге использовать константу для полей индекса"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_update_constant_map_valid(self, super_user, integration_user, provider_constructor,
                                                            diagram_constructor):
        with allure.step("Получение информации"):
            in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
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

        with allure.step("Обновление узла с использованием констант для полей индекса"):
            cond_var_1 = insert_input_var_mapping(var_name=5, type_id="2",
                                                  providers_column_name=columnns_for_cond[0].columnName,
                                                  providers_column_data_type=columnns_for_cond[0].dataType,
                                                  is_literal=True)
            cond_var_2 = insert_input_var_mapping(var_name=4, type_id="2",
                                                  providers_column_name=columnns_for_cond[1].columnName,
                                                  providers_column_data_type=columnns_for_cond[1].dataType,
                                                  is_literal=True)
            update_var = insert_input_var_mapping(var_name=in_out_v.parameterName, type_id=IntValueType.long.value,
                                                  providers_column_name=columnns_for_upd[0].columnName,
                                                  providers_column_data_type=columnns_for_upd[0].dataType,
                                                  param_id=in_out_v.parameterId)
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
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел, узел валиден"):
            assert node_view.validFlag

    @allure.story(
        "Узел Tarantool запись валидный при маппинге обновляемых атрибутов на константы для режима 'Обновление данных'"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы в "
        "маппинге использовать константу для обновляемых атрибутов"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_update_constant_attributes_map_valid(self, super_user, integration_user,
                                                                       provider_constructor,
                                                                       diagram_constructor):
        with allure.step("Получение информации"):
            in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
            in_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
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
        with allure.step("Обновить узел, использовать константу для обновляемых атрибутов"):
            cond_var_1 = insert_input_var_mapping(var_name="in_out_int", type_id=IntValueType.long.value,
                                                  providers_column_name=columnns_for_cond[0].columnName,
                                                  providers_column_data_type=columnns_for_cond[0].dataType,
                                                  param_id=in_out_v.parameterId)
            cond_var_2 = insert_input_var_mapping(var_name="in_int", type_id=IntValueType.long.value,
                                                  providers_column_name=columnns_for_cond[1].columnName,
                                                  providers_column_data_type=columnns_for_cond[1].dataType,
                                                  param_id=in_v.parameterId)
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
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел. Узел валиден"):
            assert node_view.validFlag

    @allure.story(
        "Узел Tarantool запись валидный при маппинге полей индекса на константы для режима "
        "'Вставка и Обновление данных'"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы в "
        "маппинге использовать константу для полей индекса"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("PRIMARY")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_str", varType="in", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_upsert_constant_map_valid(self, super_user, integration_user, provider_constructor,
                                                            diagram_constructor):
        with allure.step("Получение информации"):
            in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
            in_str_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_str"]
            node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
            provider_info = provider_constructor["provider_info"]
            columns = provider_constructor["columns"]
            searched_index = provider_constructor["index"]
            columns_for_cond = []
            column_for_upd_long: ColumnsDto = ColumnsDto.construct()
            column_for_upd_str: ColumnsDto = ColumnsDto.construct()
            for column in columns:
                if column.isPrimary:
                    if column.dataType == "long":
                        columns_for_cond.append(column)
                else:
                    if column.dataType == "long":
                        column_for_upd_long = column
                    if column.dataType == "string":
                        column_for_upd_str = column
        with allure.step("Обновить узел, использую константу для полей индекса. Режим - Вставка и обновление"):
            cond_var_1 = insert_input_var_mapping(var_name=5, type_id="2",
                                                  providers_column_name=columns_for_cond[0].columnName,
                                                  providers_column_data_type=columns_for_cond[0].dataType,
                                                  is_literal=True)
            cond_var_2 = insert_input_var_mapping(var_name=4, type_id="2",
                                                  providers_column_name=columns_for_cond[1].columnName,
                                                  providers_column_data_type=columns_for_cond[1].dataType,
                                                  is_literal=True)
            update_var_1 = insert_input_var_mapping(var_name="in_out_int", type_id=IntValueType.long.value,
                                                    providers_column_name=column_for_upd_long.columnName,
                                                    providers_column_data_type=column_for_upd_long.dataType,
                                                    param_id=in_out_v.parameterId)
            update_var_2 = insert_input_var_mapping(var_name="in_str", type_id=IntValueType.str.value,
                                                    providers_column_name=column_for_upd_str.columnName,
                                                    providers_column_data_type=column_for_upd_str.dataType,
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
        with allure.step("Проверка, что указанные данные успешно добавились в узел. Узел валиден"):
            assert node_view.validFlag

    @allure.story(
        "Узел Tarantool запись валидный при маппинге обновляемых атрибутов на константы для режима "
        "'Вставка и Обновление данных'"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы в "
        "маппинге использовать константу для обновляемых атрибутов"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("PRIMARY")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_write_node_upsert_constant_attributes_map_valid(self, super_user, integration_user,
                                                                       provider_constructor,
                                                                       diagram_constructor):
        with allure.step("Получение информации об источнике и диаграмме"):
            in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
            in_int_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
            node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
            provider_info = provider_constructor["provider_info"]
            columns = provider_constructor["columns"]
            searched_index = provider_constructor["index"]
            columns_for_cond = []
            column_for_upd_long: ColumnsDto = ColumnsDto.construct()
            column_for_upd_str: ColumnsDto = ColumnsDto.construct()
            for column in columns:
                if column.isPrimary:
                    if column.dataType == "long":
                        columns_for_cond.append(column)
                else:
                    if column.dataType == "long":
                        column_for_upd_long = column
                    if column.dataType == "string":
                        column_for_upd_str = column
        with allure.step("Обновить узел с использованием констант в маппинге обновляемых атрибутов."
                         " Режим - Вставка и обновление"):
            cond_var_1 = insert_input_var_mapping(var_name="in_out_int", type_id=IntValueType.long.value,
                                                  providers_column_name=columns_for_cond[0].columnName,
                                                  providers_column_data_type=columns_for_cond[0].dataType,
                                                  param_id=in_out_v.parameterId)
            cond_var_2 = insert_input_var_mapping(var_name="in_int", type_id=IntValueType.long.value,
                                                  providers_column_name=columns_for_cond[1].columnName,
                                                  providers_column_data_type=columns_for_cond[1].dataType,
                                                  param_id=in_int_v.parameterId)
            update_var_1 = insert_input_var_mapping(var_name=5, type_id="2",
                                                    providers_column_name=column_for_upd_long.columnName,
                                                    providers_column_data_type=column_for_upd_long.dataType,
                                                    is_literal=True)
            update_var_2 = insert_input_var_mapping(var_name="'hello'", type_id="2",
                                                    providers_column_name=column_for_upd_str.columnName,
                                                    providers_column_data_type=column_for_upd_str.dataType,
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
        with allure.step("Проверка, что указанные данные успешно добавились в узел. Узел валиден"):
            assert node_view.validFlag

    @allure.story(
        "Узел Tarantool запись валидный при маппинге обновляемых атрибутов и полей индекса на константы для режима "
        "'Вставка и Обновление данных'  при незаполненных isNullable = true"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы в "
        "маппинге использовать константу в маппинге полей индекса и для обновляемых атрибутов"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("TEST_PRIMITIVE_TYPES")
    @pytest.mark.index_type("PRIMARY")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    @allure.issue("DEV-22947")
    def test_tarantool_write_node_upsert_constant_attributes_map_nullable(self, super_user, integration_user,
                                                                          provider_constructor,
                                                                          diagram_constructor):
        with allure.step("Получение информации о диаграмме и источнике"):
            in_out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_int"]
            node_tarantool_ins: NodeViewShortInfo = diagram_constructor["nodes"]["запись тарантул"]
            provider_info = provider_constructor["provider_info"]
            columns = provider_constructor["columns"]
            searched_index = provider_constructor["index"]
            columns_null = []
            columns_for_cond = []
            column_for_upd_int: ColumnsDto = ColumnsDto.construct()
            column_for_upd_str: ColumnsDto = ColumnsDto.construct()
            column_for_upd_bool: ColumnsDto = ColumnsDto.construct()
            column_for_upd_datetime: ColumnsDto = ColumnsDto.construct()
            column_for_upd_time: ColumnsDto = ColumnsDto.construct()
            column_for_upd_date: ColumnsDto = ColumnsDto.construct()
            column_for_upd_double: ColumnsDto = ColumnsDto.construct()
            column_for_upd_float: ColumnsDto = ColumnsDto.construct()
            for column in columns:
                if column.isPrimary:
                    if column.dataType == "long":
                        columns_for_cond.append(column)
                if column.isNullable:
                    if column.dataType == "string":
                        columns_null.append(column)
                else:
                    if column.dataType == "string":
                        column_for_upd_str = column
                    if column.dataType == "float":
                        column_for_upd_float = column
                    if column.dataType == "int":
                        column_for_upd_int = column
                    if column.dataType == "boolean":
                        column_for_upd_bool = column
                    if column.dataType == "DateTime":
                        column_for_upd_datetime = column
                    if column.dataType == "Time":
                        column_for_upd_time = column
                    if column.dataType == "Date":
                        column_for_upd_date = column
                    if column.dataType == "double":
                        column_for_upd_double = column
        with allure.step("Обновить узел, используя для маппинга константы "
                         "и не заполняя значения при isNullable = true"):
            cond_var_1 = insert_input_var_mapping(var_name=333, type_id="2",
                                                  providers_column_name=columns_for_cond[0].columnName,
                                                  providers_column_data_type=columns_for_cond[0].dataType,
                                                  param_id=in_out_v.parameterId,
                                                  is_literal=True)
            update_var_1 = insert_input_var_mapping(var_name=5, type_id="2",
                                                    providers_column_name=column_for_upd_int.columnName,
                                                    providers_column_data_type=column_for_upd_int.dataType,
                                                    is_literal=True)
            update_var_2 = insert_input_var_mapping(var_name="'hello'", type_id="2",
                                                    providers_column_name=column_for_upd_str.columnName,
                                                    providers_column_data_type=column_for_upd_str.dataType,
                                                    is_literal=True)
            update_var_3 = insert_input_var_mapping(var_name="'true'", type_id="2",
                                                    providers_column_name=column_for_upd_bool.columnName,
                                                    providers_column_data_type=column_for_upd_bool.dataType,
                                                    is_literal=True)
            update_var_4 = insert_input_var_mapping(var_name="'2023-12-22 02:01:01.456'", type_id="2",
                                                    providers_column_name=column_for_upd_datetime.columnName,
                                                    providers_column_data_type=column_for_upd_datetime.dataType,
                                                    is_literal=True)
            update_var_5 = insert_input_var_mapping(var_name="'02:01:01'", type_id="2",
                                                    providers_column_name=column_for_upd_time.columnName,
                                                    providers_column_data_type=column_for_upd_time.dataType,
                                                    is_literal=True)
            update_var_6 = insert_input_var_mapping(var_name="'2023-12-23'", type_id="2",
                                                    providers_column_name=column_for_upd_date.columnName,
                                                    providers_column_data_type=column_for_upd_date.dataType,
                                                    is_literal=True)
            update_var_7 = insert_input_var_mapping(var_name=9.8, type_id="2",
                                                    providers_column_name=column_for_upd_float.columnName,
                                                    providers_column_data_type=column_for_upd_float.dataType,
                                                    is_literal=True)
            update_var_8 = insert_input_var_mapping(var_name=9.9, type_id="2",
                                                    providers_column_name=column_for_upd_double.columnName,
                                                    providers_column_data_type=column_for_upd_double.dataType,
                                                    is_literal=True)
            update_var_9 = insert_input_var_mapping(var_name="", type_id="2",
                                                    providers_column_name=columns_null[0].columnName,
                                                    providers_column_data_type=columns_null[0].dataType, is_null=True)
            tarantool_node = tarantool_insert_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                                        source_id=provider_info.sourceId,
                                                        table_name="TEST_PRIMITIVE_TYPES",
                                                        selected_index_name=searched_index.indexName,
                                                        query_type=QueryType1.MERGE,
                                                        input_vars_update_mapping=[update_var_1, update_var_2,
                                                                                   update_var_3, update_var_4,
                                                                                   update_var_5, update_var_6,
                                                                                   update_var_7, update_var_8,
                                                                                   update_var_9],
                                                        input_vars_cond_mapping=[cond_var_1])
            update_node(super_user, node_id=node_tarantool_ins.nodeId, body=tarantool_node,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=tarantool_node.nodeTypeId,
                            properties=tarantool_node.properties))
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_ins.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел, узел валиден"):
            assert node_view.validFlag
