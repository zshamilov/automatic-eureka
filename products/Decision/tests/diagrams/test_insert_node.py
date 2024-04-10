import uuid

import allure
from requests import HTTPError

from products.Decision.framework.db_framework import db_model
from products.Decision.utilities.db_tables_utils import get_column_properties, \
    get_db_column_name, get_nullable_columns, get_primary_key
from products.Decision.framework.model import ResponseDto, NodeValidateDto, ColumnsDto, AvailableTypesRequestDto
from products.Decision.framework.steps.decision_steps_data_provider_api import post_data_provider_types_by_column
from products.Decision.framework.steps.decision_steps_nodes import create_node, \
    delete_node_by_id, validate_node
from products.Decision.runtime_tests.runtime_fixtures.jdbc_write_fixtures import *
from products.Decision.utilities.custom_models import VariableParams


@allure.epic("Диаграммы")
@allure.feature("Узел сохранения данных")
class TestDiagramsInsertNode:
    @allure.story(
        "К узлу сохранения данных возможно добавить источник данных"
    )
    @allure.title(
        "Обновить узел сохранения данных добавив к нему валидный источник данных"
    )
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    @pytest.mark.scenario("DEV-15450")
    @pytest.mark.smoke
    def test_create_diagram_with_insert(self, db_user, super_user, diagram_insert_2):
        temp_version_id = diagram_insert_2["temp_version_id"]
        provider: DataProviderGetFullView = diagram_insert_2["provider"]
        insert_node_id = diagram_insert_2["insert_node_id"]
        diagram_param = diagram_insert_2["diagram_param"]
        schema_name = diagram_insert_2["schema_name"]
        table_name = diagram_insert_2["table_name"]
        columns = diagram_insert_2["columns"]
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
                                                   schema_name=schema_name,
                                                   input_vars_update_mapping=[insert_var_update])
        update_body = insert_node_construct(x=700, y=202.22915649414062,
                                            temp_version_id=temp_version_id,
                                            properties=insert_properties,
                                            operation="update")
        update_node(super_user, node_id=insert_node_id, body=update_body)
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, insert_node_id).body
            )
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert node_view.properties["dataProviderUuid"] == str(provider.sourceId) \
                   and node_view.validFlag

    @allure.story("Узел сохранения данных создаётся")
    @allure.title(
        "Создать диаграмму с узлом сохранения данных без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15450")
    @pytest.mark.smoke
    def test_create_insert_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
        with allure.step("Создание узла узла сохранения"):
            node_insert = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id)
            node_insert_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_insert).body
            )
            node_insert_id = node_insert_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла сохранения корректен и равен 5-сохранение данных"
        ):
            assert diagram.nodes[str(node_insert_id)].nodeTypeId == 5

    @allure.story("Узел сохранения удаляется")
    @allure.title(
        "Создать диаграмму с узлом сохранения без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.scenario("DEV-15450")
    @pytest.mark.smoke
    def test_delete_node_insert(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
        with allure.step("Создание узла сохранения данных"):
            node_insert = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id)
            node_insert_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_insert).body
            )
            node_insert_id = node_insert_response.uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_insert_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_insert_id).status == 404

    @allure.story("Есть валидация на существующий источник данных")
    @allure.title("Создать диаграмму с узлом сохранения с несуществующим источником данных")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_random_source(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
            int_column_properties = get_column_properties(columns, "integer")
        with allure.step("Обновление узла сохранения с несуществующим источником данных"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name=int_column_properties.columnName,
                                                         providers_column_data_type="integer",
                                                         is_null=int_column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=int_column_properties.isPrimary)
            random_source_id = str(uuid.uuid4())
            insert_properties = insert_node_properties(source_id=random_source_id,
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["nodeValidationMap"]["dataProviderUuid"] == \
                   f"Источника данных с идентификатором - {random_source_id} не найдено"

    @allure.story("Есть валидация на существующее имя таблицы")
    @allure.title("Создать диаграмму с узлом сохранения с несуществующим названием таблицы ")
    @pytest.mark.scenario("DEV-6398")
    @allure.issue(url="DEV-24221")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_table_name_incorrect(self, db_user,
                                         super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
            not_exist_table = "not_a_table_name"
            int_column_properties = get_column_properties(columns, "integer")
        with allure.step("Обновление узла сохранения с несуществующим названием таблицы"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name=int_column_properties.columnName,
                                                         providers_column_data_type=int_column_properties.dataType,
                                                         is_null=int_column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=int_column_properties.isPrimary)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=not_exist_table,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["nodeValidationMap"]["tableName"] == \
                   f"Таблица с названием {not_exist_table} не найдена"

    @allure.story("Есть валидация на существующее поле таблицы")
    @allure.title(
        "Создать диаграмму с узлом сохранения с несуществующим названием столбца ")
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-21099")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_column_name_incorrect(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]

            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
            int_column_properties = get_column_properties(columns, "integer")
        with allure.step("Обновление узла сохранения с несуществующим названием столбца"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name="not_a_column_name",
                                                         providers_column_data_type=int_column_properties.dataType,
                                                         is_null=int_column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=int_column_properties.isPrimary)
            row_key = insert_var_update.rowKey

            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["nodeValidationMap"]["inputVariablesUpdateMapping"][
                       row_key]["nodeVariable.columnName"] == "Атрибут должен существовать в таблице"

    @allure.story("Предусмотрена проверка на обязательность заполнения источника данных независимо от "
                  "queryType")
    @allure.title(
        "Создать диаграмму с узлом сохранения без дата-провайдера со всеми  query_type")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.parametrize("query_type", [QueryType1.INSERT, QueryType1.UPDATE, QueryType1.MERGE])
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_query_type(self, db_user, super_user, diagram_insert_2, query_type):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]

            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
            int_column_properties = get_column_properties(columns, "integer")
        with allure.step("Обновление узла сохранения без дата-провайдера, с разным  query_type"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name=int_column_properties.columnName,
                                                         providers_column_data_type=int_column_properties.dataType,
                                                         is_null=int_column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=int_column_properties.isPrimary)
            insert_properties = insert_node_properties(source_id="",
                                                       table_name=table_name,
                                                       query_type=query_type,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)

        with allure.step("Получение ошибки и ее описание"):
            valid_message = validation_response.validationPayload[
                "nodeValidationMap"]["dataProviderUuid"]
            assert valid_message == "Поле обязательно для заполнения" and validation_response.httpCode == 422

    @allure.story("Предусмотрена проверка на обязательность заполнения таблицы независимо от "
                  "queryType")
    @allure.title(
        "Создать диаграмму с узлом сохранения без таблицы со всеми  query_type")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    @pytest.mark.parametrize("query_type", [QueryType1.INSERT, QueryType1.UPDATE, QueryType1.MERGE])
    def test_insert_without_table_name(self, db_user, super_user, diagram_insert_2, query_type):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]

            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
            int_column_properties = get_column_properties(columns, "integer")
        with allure.step("Обновление узла сохранения без table_name"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name=int_column_properties.columnName,
                                                         providers_column_data_type=int_column_properties.dataType,
                                                         is_null=int_column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=int_column_properties.isPrimary)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name="",
                                                       query_type=query_type,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["nodeValidationMap"]["tableName"] \
                   == "Поле обязательно для заполнения"

    @allure.story("Предусмотрена проверка, что указанная в маппинге переменная диаграммы существует")
    @allure.issue(url="DEV-9679")
    @allure.title("Создать диаграмму с узлом сохранения, в маппинге указать несуществующую переменную")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_non_existent_var_name(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]

            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
            int_column_properties = get_column_properties(columns, "integer")
        with allure.step("Обновление узла сохранения с несуществующим именем в var_name"):
            non_existent_name = "not_variable_name"
            insert_var_update = insert_input_var_mapping(var_name=non_existent_name,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name=int_column_properties.columnName,
                                                         providers_column_data_type=int_column_properties.dataType,
                                                         is_null=int_column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=int_column_properties.isPrimary)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
            row_key = insert_var_update.rowKey
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Получение ошибки и ее описание"):
            valid_message = validation_response.validationPayload["nodeValidationMap"]["inputVariablesUpdateMapping"][
                row_key]["variableName"]
            assert validation_response.httpCode == 422 \
                   and valid_message == "Переменная не найдена или не была рассчитана"

    @allure.story("Предусмотрена проверка, что тип указанной в маппинге переменной соответствует типу столбца")
    @allure.title("Создать диаграмму с узлом сохранения, в маппинге указать переменную типа, не соответствующего типу "
                  "столбца таблицы")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_incorrect_providers_column_type(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
        with allure.step("Получение информации об источнике"):
            db_table = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            column_properties = get_column_properties(columns, "character varying")
            schema_name = diagram_insert_2["schema_name"]
        with allure.step("Обновление узла сохранения с невалидным providers_column_data_type"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id=diagram_param.typeId,
                                                         providers_column_name=column_properties.columnName,
                                                         providers_column_data_type=column_properties.dataType,
                                                         is_null=column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=column_properties.isPrimary)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=db_table,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
            row_key = insert_var_update.rowKey
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Получение ошибки и ее описание"):
            valid_message = validation_response.validationPayload["nodeValidationMap"]["inputVariablesUpdateMapping"][
                row_key]["variableName"]
            assert validation_response.httpCode == 422 and valid_message == "Типы данных не совпадают"

    @allure.story("Предусмотрена проверка, что колонка таблицы указана один раз")
    @allure.title("В узле сохранения данных дважды произвести маппинг на одну и ту же колонку, проверить, "
                  "что вернулась ошибка валидации")
    @pytest.mark.scenario("DEV-6398")
    @allure.issue(url="DEV-24397")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_two_vars_same_column(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            column_properties = get_column_properties(columns, "integer")
            schema_name = diagram_insert_2["schema_name"]
        with allure.step("Обновление узла сохранения на две переменные, ссылающиеся на одинаковое имя колонки"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name=column_properties.columnName,
                                                         providers_column_data_type=column_properties.dataType,
                                                         is_null=column_properties.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=column_properties.isPrimary)
            insert_var_update2 = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                          is_arr=False, is_compl=False,
                                                          type_id="1",
                                                          providers_column_name=column_properties.columnName,
                                                          providers_column_data_type=column_properties.dataType,
                                                          is_null=column_properties.isNullable,
                                                          is_dict=False,
                                                          is_literal=False,
                                                          param_id=diagram_param.parameterId,
                                                          is_primary=column_properties.isPrimary)
            row_key_var2 = insert_var_update2.rowKey
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update,
                                                                                  insert_var_update2])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Проверяем что дубли имён колонок найдены"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["nodeValidationMap"]["inputVariablesUpdateMapping"][
                       row_key_var2]["nodeVariable.columnName"] == "Существуют дубли в именах переменных"

    @allure.story("Нет ошибки при маппинге одной и той же переменной на входной атрибут узла")
    @allure.title("Возможно произвести маппинг на одну и ту же переменную")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_same_vars(self, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]

            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
            int_column1, int_column2 = list(filter(lambda column: column.dataType == "integer", columns))[:2]
            int_column1: ColumnsDto
            int_column2: ColumnsDto

        with allure.step("Обновление узла сохранения с мапингом на одну и ту же переменную"):
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id="1",
                                                         providers_column_name=int_column1.columnName,
                                                         providers_column_data_type="integer",
                                                         is_null=int_column1.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         param_id=diagram_param.parameterId,
                                                         is_primary=int_column1.isPrimary)
            insert_var_update2 = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                          is_arr=False, is_compl=False,
                                                          type_id="1",
                                                          providers_column_name=int_column2.columnName,
                                                          providers_column_data_type="integer",
                                                          is_null=int_column2.isNullable,
                                                          is_dict=False,
                                                          is_literal=False,
                                                          param_id=diagram_param.parameterId,
                                                          is_primary=int_column2.isPrimary)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update,
                                                                                  insert_var_update2])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Проверяем что узел валиден"):
            assert validation_response.httpCode == 200 and validation_response.operation == "validate"

    @allure.story("Предусмотрена проверка на то, что настроен маппинг для всех параметров узла")
    @allure.title("Добавляем в мапинг столбец таблицы и не заполняем его")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.skip("obsolete")
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_var_name_not_empty(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            schema_name = diagram_insert_2["schema_name"]
            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            int_column = list(filter(lambda column: column.dataType == "integer", columns)).pop().columnName

        with allure.step("Обновление узла сохранения с неуказанным именем переменной для маппинга"):
            insert_var_update = insert_input_var_mapping(var_name="",
                                                         is_arr=False, is_compl=False,
                                                         type_id="",
                                                         providers_column_name=int_column,
                                                         providers_column_data_type="integer",
                                                         is_dict=False,
                                                         simple_name_val="",
                                                         full_path_val="")
            row_key = insert_var_update.rowKey

            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["nodeValidationMap"]["inputVariablesUpdateMapping"] \
                       [row_key]["variableName"] == "Поле обязательно для заполнения"

    @allure.story("Предусмотрена проверка, что в режиме вставки настроен маппинг для всех обязательных полей "
                  "таблицы")
    @allure.title("В режиме вставка добавить в маппинг все поля таблицы и, не заполняя его, провалидировать, "
                  "проверить, что вернулась ошибка для обязательных полей")
    @pytest.mark.scenario("DEV-19560")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.default_pk_autoincrement_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_required_not_empty(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            table_name = diagram_insert_2["table_name"]
            schema_name = diagram_insert_2["schema_name"]
            columns = diagram_insert_2["columns"]
            db_table_columns = diagram_insert_2["db_table"].columns
        with allure.step("Обновление узла сохранения со всеми полями и незаполненным маппингом"):
            insert_mapping, row_keys, required_column_names = [], [], []
            for column in columns:
                insert_var_update = insert_input_var_mapping(var_name="",
                                                             is_arr=False, is_compl=False,
                                                             type_id="",
                                                             providers_column_name=column.columnName,
                                                             providers_column_data_type=column.dataType,
                                                             is_null=column.isNullable,
                                                             is_dict=False,
                                                             is_literal=False,
                                                             is_primary=column.isPrimary
                                                             )
                insert_mapping.append(insert_var_update)
                if column.isPrimary or not column.isNullable:
                    row_keys.append(insert_var_update.rowKey)
                    required_column_names.append(insert_var_update.nodeVariable.columnName)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=insert_mapping)
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Получение обязательных полей БД"):
            required_db_column_names = []
            for column in db_table_columns:
                if not column.nullable or column.primary_key:
                    if column.autoincrement != True and column.server_default is None:
                        required_db_column_names.append(column.name)
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)

        with allure.step("Получение ошибки и ее описания"):
            assert validation_response.httpCode == 422 \
                   and all(validation_response.validationPayload["nodeValidationMap"]["inputVariablesUpdateMapping"][
                               row_key]["variableName"] == "Поле обязательно для заполнения" for row_key in row_keys) \
                   and required_column_names == required_db_column_names

    @allure.story("Предусмотрена проверка, что в режиме вставки все обязательные поля указаны в маппинге")
    @allure.title("В режиме вставка добавить в маппинг необязательное поле, проверить, что вернулась ошибка")
    @pytest.mark.scenario("DEV-19560")
    @allure.issue(url="DEV-24606")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.default_pk_autoincrement_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_all_required_vars_exists(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
            table_name = diagram_insert_2["table_name"]
            schema_name = diagram_insert_2["schema_name"]
            columns = diagram_insert_2["columns"]
        with allure.step("Обновление узла сохранения с одним необязательным полем"):
            with allure.step("Получение необязательного поля"):
                not_required_columns = get_nullable_columns(columns)
                long_not_required_column = get_column_properties(not_required_columns, "bigint")
            with allure.step("Обновление узла"):
                insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                             is_arr=False, is_compl=False,
                                                             type_id=diagram_param.typeId,
                                                             providers_column_name=long_not_required_column.columnName,
                                                             providers_column_data_type=long_not_required_column.dataType,
                                                             is_null=long_not_required_column.isNullable,
                                                             is_dict=False,
                                                             is_literal=False,
                                                             is_primary=long_not_required_column.isPrimary
                                                             )
                insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                           table_name=table_name,
                                                           query_type=QueryType1.INSERT,
                                                           schema_name=schema_name,
                                                           input_vars_update_mapping=[insert_var_update])
                update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                    temp_version_id=temp_version_id,
                                                    properties=insert_properties,
                                                    operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)

        with allure.step("Получение ошибки и ее описания"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["commonNodeValidationMessages"] == "Не для всех " \
                                                                                                "обязательных полей " \
                                                                                                "указано значение"

    @allure.story("Предусмотрена проверка, что в режиме обновления, в случае отсутствия в маппинге обязательных полей,"
                  "нет ошибки валидации")
    @allure.title("В режиме обновления добавить в маппинг условий отбора и обновляемых атрибутов необязательное поле, "
                  "проверить, что НЕ вернулась ошибка для обязательных полей")
    @pytest.mark.scenario("DEV-19560")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.default_pk_autoincrement_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_update_without_required(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
            schema_name = diagram_insert_2["schema_name"]
            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
        with allure.step("Обновление узла сохранения с необязательным атрибутом"):
            with allure.step("Получение необязательного поля"):
                not_required_columns = get_nullable_columns(columns)
                long_not_required_column = get_column_properties(not_required_columns, "bigint")
            insert_var_condition = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                            is_arr=False, is_compl=False,
                                                            type_id=diagram_param.typeId,
                                                            providers_column_name=long_not_required_column.columnName,
                                                            providers_column_data_type=long_not_required_column.dataType,
                                                            is_null=long_not_required_column.isNullable,
                                                            is_dict=False,
                                                            is_literal=False,
                                                            is_primary=long_not_required_column.isPrimary
                                                            )
            insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                         is_arr=False, is_compl=False,
                                                         type_id=diagram_param.typeId,
                                                         providers_column_name=long_not_required_column.columnName,
                                                         providers_column_data_type=long_not_required_column.dataType,
                                                         is_null=long_not_required_column.isNullable,
                                                         is_dict=False,
                                                         is_literal=False,
                                                         is_primary=long_not_required_column.isPrimary
                                                         )
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.UPDATE,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update],
                                                       input_vars_condition_mapping=[insert_var_condition])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
        with allure.step("Проверка, что узел валидный"):
            assert validation_response.httpCode == 200 and validation_response.operation == "validate"

    @allure.story("Предусмотрена проверка, что в режимах обновления и вставки и обновления настроен маппинг для всех "
                  "обязательных полей таблицы")
    @allure.title("В режимах вставки и вставки и обновления добавить в маппинг условий отбора колонку PK, а в маппинг "
                  "обновляемых - все остальные и, не заполняя маппинги, провалидировать,проверить, что вернулась "
                  "ошибка для обязательных полей")
    @pytest.mark.scenario("DEV-19560")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.default_pk_autoincrement_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.parametrize("query_type", [QueryType1.UPDATE, QueryType1.MERGE])
    @pytest.mark.nodes(["запись"])
    def test_insert_upsert_required_not_empty(self, db_user, super_user, diagram_insert_2, query_type):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            schema_name = diagram_insert_2["schema_name"]
            table_name = diagram_insert_2["table_name"]
            columns = diagram_insert_2["columns"]
            db_table_columns = diagram_insert_2["db_table"].columns
        with allure.step("Обновление узла сохранения с полем PK в маппинге условий и остальными полями в обновляемых "
                         "атрибутах и незаполненным маппингом"):
            insert_mapping, insert_condition_mapping, row_keys_req_upd, required_col_names_upd = [], [], [], []
            primary_key_column = get_primary_key(columns)
            insert_var_condition = insert_input_var_mapping(var_name="",
                                                            is_arr=False, is_compl=False,
                                                            type_id="",
                                                            providers_column_name=primary_key_column.columnName,
                                                            providers_column_data_type=primary_key_column.dataType,
                                                            is_null=primary_key_column.isNullable,
                                                            is_dict=False,
                                                            is_literal=False,
                                                            is_primary=primary_key_column.isPrimary
                                                            )
            row_key_cond = insert_var_condition.rowKey
            columns_without_pk = list(
                filter(lambda column: column.columnName != primary_key_column.columnName, columns))
            for column in columns_without_pk:
                insert_var_update = insert_input_var_mapping(var_name="",
                                                             is_arr=False, is_compl=False,
                                                             type_id="",
                                                             providers_column_name=column.columnName,
                                                             providers_column_data_type=column.dataType,
                                                             is_null=column.isNullable,
                                                             is_dict=False,
                                                             is_literal=False,
                                                             is_primary=column.isPrimary
                                                             )
                insert_mapping.append(insert_var_update)
                if not column.isNullable:
                    required_col_names_upd.append(column.columnName)
                    row_keys_req_upd.append(insert_var_update.rowKey)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=query_type,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=insert_mapping,
                                                       input_vars_condition_mapping=[insert_var_condition])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Получение обязательных полей БД"):
            required_db_column_names = []
            for column in db_table_columns:
                if not column.nullable or column.primary_key:
                    if column.autoincrement != True and column.server_default is None:
                        required_db_column_names.append(column.name)
            with allure.step("Получение обязательных полей без PK"):
                required_db_column_names_not_pk = list(
                    filter(lambda column: column != primary_key_column.columnName, required_db_column_names))
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)

        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and all(validation_response.validationPayload["nodeValidationMap"]["inputVariablesUpdateMapping"][
                               row_key]["variableName"] == "Поле обязательно для заполнения" for row_key in
                           row_keys_req_upd) \
                   and validation_response.validationPayload["nodeValidationMap"]["inputVariablesConditionMapping"][
                       row_key_cond]["variableName"] == "Поле обязательно для заполнения" \
                   and required_col_names_upd == required_db_column_names_not_pk

    @allure.story("Предусмотрена проверка, что в режиме вставки и обновления в маппинге обновления указаны все "
                  "обязательные поля таблицы")
    @allure.title("В режиме вставки и обновления добавить в маппинг обновляемых атрибутов только необязательне поля, "
                  "провалидировать,проверить, что вернулась ошибка")
    @pytest.mark.scenario("DEV-19560")
    @allure.issue(url="DEV-24606")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.default_pk_autoincrement_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.float.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_upsert_all_required_vars_exists(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
            table_name = diagram_insert_2["table_name"]
            schema_name = diagram_insert_2["schema_name"]
            columns = diagram_insert_2["columns"]
        with allure.step("Обновление узла сохранения с необязательным полем в обновляемых атрибутах и заполненным "
                         "маппингом"):
            with allure.step("Получение необязательного поля"):
                not_required_columns = get_nullable_columns(columns)
                long_not_required_column = get_column_properties(not_required_columns, "bigint")
            with allure.step("Получение PK"):
                primary_key_column = get_primary_key(columns)
            insert_var_condition = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                            is_arr=False, is_compl=False,
                                                            type_id=diagram_param.typeId,
                                                            providers_column_name=primary_key_column.columnName,
                                                            providers_column_data_type=primary_key_column.dataType,
                                                            is_null=primary_key_column.isNullable,
                                                            is_dict=False,
                                                            is_literal=False,
                                                            is_primary=primary_key_column.isPrimary
                                                            )
            insert_var_update = insert_input_var_mapping(var_name="11",
                                                         is_arr=False, is_compl=False,
                                                         type_id="7",
                                                         providers_column_name=long_not_required_column.columnName,
                                                         providers_column_data_type=long_not_required_column.dataType,
                                                         is_null=long_not_required_column.isNullable,
                                                         is_dict=False,
                                                         is_literal=True,
                                                         is_primary=long_not_required_column.isPrimary
                                                         )
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.MERGE,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=[insert_var_update],
                                                       input_vars_condition_mapping=[insert_var_condition])
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)

        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["commonNodeValidationMessages"] == "Не для всех " \
                                                                                                "обязательных полей " \
                                                                                                "указано значение"

    @allure.story("Предусмотрена проверка, что в режиме вставки и обновления в условиях отбора указан PK")
    @allure.title("Обновить узел сохранения в режиме вставка и обновление, передать пустые условия отбора, проверить, "
                  "что вернулась ошибка")
    @pytest.mark.scenario("DEV-19560")
    @allure.issue(url="DEV-24606")
    @pytest.mark.smoke
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_insert_upsert_pk_exists(self, db_user, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            diagram_param = diagram_insert_2["diagram_param"]
            table_name = diagram_insert_2["table_name"]
            schema_name = diagram_insert_2["schema_name"]
            columns = diagram_insert_2["columns"]
        with allure.step("Обновление узла сохранения с пустыми условиями отбора"):
            with allure.step("Получение необязательного поля"):
                not_required_columns = get_nullable_columns(columns)
                int_not_required_column = get_column_properties(not_required_columns, "integer")
            with allure.step("Обновление узла"):
                insert_var_update = insert_input_var_mapping(var_name=diagram_param.parameterName,
                                                             is_arr=False, is_compl=False,
                                                             type_id=diagram_param.typeId,
                                                             providers_column_name=int_not_required_column.columnName,
                                                             providers_column_data_type=int_not_required_column.dataType,
                                                             is_null=int_not_required_column.isNullable,
                                                             is_dict=False,
                                                             is_literal=False,
                                                             is_primary=int_not_required_column.isPrimary
                                                             )
                insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                           table_name=table_name,
                                                           query_type=QueryType1.MERGE,
                                                           schema_name=schema_name,
                                                           input_vars_update_mapping=[insert_var_update],
                                                           input_vars_condition_mapping=[])
                update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                    temp_version_id=temp_version_id,
                                                    properties=insert_properties,
                                                    operation="update")
        with allure.step("Валидация узла сохранения"):
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=insert_node_id,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)

        with allure.step("Получение ошибки и ее описание"):
            assert validation_response.httpCode == 422 \
                   and validation_response.validationPayload["commonNodeValidationMessages"] == "Таблица Условия " \
                                                                                                "отбора записей не " \
                                                                                                "может быть пустой"

    @allure.story("Для колонки БД возвращается корректный тип, доступный для маппинга")
    @allure.title("Создать узел сохранения данных с таблицей со всеми стандартными типами, проверить, что для каждого "
                  "поля таблицы вернулся корректный тип")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.default_pk_autoincrement_table.name)
    @pytest.mark.scenario("DEV-15450")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    @pytest.mark.smoke
    def test_insert_correct_types(self, super_user, diagram_insert_2):
        with allure.step("Получение информации о диаграмме"):
            temp_version_id = diagram_insert_2["temp_version_id"]
            provider: DataProviderGetFullView = diagram_insert_2["provider"]
            insert_node_id = diagram_insert_2["insert_node_id"]
            table_name = diagram_insert_2["table_name"]
            db_table = diagram_insert_2["db_table"]
            columns = diagram_insert_2["columns"]
            schema_name = diagram_insert_2["schema_name"]
        with allure.step("Обновление узла"):
            insert_mapping = []
            for column in columns:
                insert_var_update = insert_input_var_mapping(var_name="",
                                                             is_arr=False, is_compl=False,
                                                             type_id="",
                                                             providers_column_name=column.columnName,
                                                             providers_column_data_type=column.dataType,
                                                             is_null=column.isNullable,
                                                             is_dict=False,
                                                             is_literal=False,
                                                             is_primary=column.isPrimary
                                                             )
                insert_mapping.append(insert_var_update)
            insert_properties = insert_node_properties(source_id=str(provider.sourceId),
                                                       table_name=table_name,
                                                       query_type=QueryType1.INSERT,
                                                       schema_name=schema_name,
                                                       input_vars_update_mapping=insert_mapping)
            update_body = insert_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=temp_version_id,
                                                properties=insert_properties,
                                                operation="update")
            update_node(super_user, node_id=insert_node_id, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, insert_node_id).body
            )
        with allure.step("Проверка, что для каждого поля таблицы возвращается корректный тип переменной диаграммы"):
            with allure.step(
                    "Формирование body для получения типа переменной диаграммы, подходящей для маппинга для текущей "
                    "колонки"):
                for out_var_map in node_view.properties["inputVariablesUpdateMapping"]:
                    types_by_column_construct = AvailableTypesRequestDto.construct(sourceId=provider.sourceId,
                                                                                   typesRetrieveType="TABLE",
                                                                                   columnName=
                                                                                   out_var_map["nodeVariable"][
                                                                                       "columnName"],
                                                                                   tableName=table_name,
                                                                                   scheme=schema_name)
                    with allure.step("Получение вернувшегося типа"):
                        diagram_type = post_data_provider_types_by_column(super_user, types_by_column_construct).body

                    with allure.step("Проверка, что вернувшийся тип соответствует колонке"):
                        with allure.step("Получение имени колонки, которой соответствует вернувшийся тип"):
                            cur_attr_db_column_name = get_db_column_name(db_table, type_id=diagram_type[0])
                        assert cur_attr_db_column_name == out_var_map["nodeVariable"]["columnName"]
