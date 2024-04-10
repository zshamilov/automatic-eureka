import uuid

import allure
from requests import HTTPError

from products.Decision.utilities.db_tables_utils import get_db_column_name
from products.Decision.framework.model import NodeViewWithVariablesDto, NodeValidateDto, SqlValidationApiDto, \
    AvailableTypesRequestDto
from products.Decision.framework.steps.decision_steps_data_provider_api import post_data_provider_types_by_column
from products.Decision.framework.steps.decision_steps_diagram import validate_diagram, \
    update_diagram_parameters
from products.Decision.framework.steps.decision_steps_nodes import create_node, get_node_by_id, \
    delete_node_by_id, validate_node
from products.Decision.framework.steps.decision_steps_validate_api import sql_validation_query
from products.Decision.runtime_tests.runtime_fixtures.jdbc_read_fixtures import *
from products.Decision.utilities.custom_models import VariableParams


@allure.epic("Диаграммы")
@allure.feature("Узел чтения")
class TestDiagramsReadNode:
    @allure.story("Узел чтения данных создаётся")
    @allure.title(
        "Создать диаграмму с узлом чтения данных без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15449")
    @pytest.mark.smoke
    def test_create_read_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
        with allure.step("Создание узла узла чтения"):
            node_read = read_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_read_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_read).body
            )
            node_read_id = node_read_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла рассчёта корректен и равен 4-чтение данных"
        ):
            assert diagram.nodes[str(node_read_id)].nodeTypeId == 4

    @allure.story("Узел чтения удаляется")
    @allure.title(
        "Создать диаграмму с узлом чтения без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.scenario("DEV-15449")
    @pytest.mark.smoke
    def test_delete_node_read(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
        with allure.step("Создание узла узла чтения"):
            node_read = read_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_read_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_read).body
            )
            node_read_id = node_read_response.uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_read_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert get_node_by_id(super_user, node_read_id).status == 404

    @allure.story(
        "В узле чтения возможно добавить источник данных и выбрать поле из таблицы"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы"
    )
    @pytest.mark.scenario("DEV-15449")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node(self, super_user, diagram_read_2):
        node_read: NodeViewShortInfo = diagram_read_2["node_read"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_read_2["param"]
        temp_version_id = diagram_read_2["temp_version_id"]
        provider: DataProviderGetFullView = diagram_read_2["data_provider"]
        db_table = diagram_read_2["db_table"]
        table_name = db_table.name
        column_name = get_db_column_name(db_table, diagram_param)

        with allure.step("Обновление узла чтения"):
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
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step("Проверка, что указанные данные успешно добавились в узел, и узел валидный"):
            assert node_view.properties["dataProviderUuid"] == provider.sourceId and \
                   node_view.properties["outputVariablesMapping"][0]["nodeVariable"] == column_name and \
                   node_view.properties["selectedTableNames"][0] == table_name \
                   and node_view.validFlag

    @allure.story(
        "Предусмотрена проверка на то, что настроен маппинг для всех параметров узла"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы с"
        " не заполненным мапингом"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue(url="DEV-10325")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    @pytest.mark.smoke
    def test_create_diagram_with_read_node_without_mapping(self, super_user, diagram_read_2):
        node_read: NodeViewShortInfo = diagram_read_2["node_read"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_read_2["param"]
        temp_version_id = diagram_read_2["temp_version_id"]
        provider: DataProviderGetFullView = diagram_read_2["data_provider"]
        db_table = diagram_read_2["db_table"]
        table_name = db_table.name
        column_name = get_db_column_name(db_table, diagram_param)

        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name="",
                                               type_id="",
                                               node_variable=column_name,
                                               is_jdbc_arr_key=False)
            mapping_raw = output_var_mapping.rowKey
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=f"select {column_name}" + " \n" + f"from {table_name}",
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=node_read.nodeId,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение узла чтения данных"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step("Проверка, что валидация возвращает ошибку из-за незаполненного маппинга, и узел невалиден"):
            assert validation_response.validationPayload["nodeValidationMap"]["outputVariablesMapping"][mapping_raw][
                       "variableName"] \
                   == "Поле обязательно для заполнения" \
                   and not node_view.validFlag

    @allure.story(
        "Предусмотрена проверка на то, что типы атрибутов запроса и элементов диаграммы в разделе “Маппинг элементов”"
        " соответствуют друг другу"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать поле из таблицы "
        "с  маппингом на одну переменную другого типа"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["чтение"])
    @pytest.mark.smoke
    def test_create_diagram_with_read_node_mapping_one_type(self, super_user, create_db_all_tables_and_scheme,
                                                            provider_constructor, diagram_constructor):
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        temp_version_id = diagram_constructor["temp_version_id"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        column_name = get_db_column_name(db_table, type_id="1")
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id="2",
                                               node_variable=column_name,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            mapping_raw = output_var_mapping.rowKey
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=f"select {column_name} " + " \n" + f"from {table_name}",
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=node_read.nodeId,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение узла чтения данных"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step(
                "Проверка, что валидация возвращает ошибку из-за несоответствия типов данных, и узел невалиден"):
            assert validation_response.validationPayload["nodeValidationMap"]["outputVariablesMapping"][mapping_raw][
                       "variableName"] \
                   == "Типы данных не совпадают" \
                   and not node_view.validFlag

    @allure.story(
        "Предусмотрена проверка, что нет маппинга выходных атрибутов на одну и ту же переменную"
    )
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать 2 поля из таблицы "
        "с  маппингом на одну переменную"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node_mapping_one(self, super_user, create_db_all_tables_and_scheme,
                                                       provider_constructor, diagram_constructor):
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        temp_version_id = diagram_constructor["temp_version_id"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        column_name = get_db_column_name(db_table, diagram_param)
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id="2",
                                               node_variable=column_name,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            output_var_mapping2 = read_variable(is_arr=False,
                                                is_compl=False,
                                                is_dict=False,
                                                var_name=diagram_param.parameterName,
                                                type_id="2",
                                                node_variable=column_name,
                                                is_jdbc_arr_key=False,
                                                param_id=diagram_param.parameterId)
            mapping_raw = output_var_mapping2.rowKey
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=f"select {column_name} " + " \n" + f"from {table_name}",
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping, output_var_mapping2],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=node_read.nodeId,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение узла чтения данных"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step("Проверка, что валидация возвращает ошибку из-за существующих дублей, и узел невалиден"):
            assert validation_response.validationPayload["nodeValidationMap"]["outputVariablesMapping"][mapping_raw][
                       "variableName"] \
                   == "Существуют дубли в именах переменных" \
                   and not node_view.validFlag

    @allure.story(
        "Предусмотрена проверка на то, что атрибут, указанный в outputVariablesMapping keyTable, упомянут в описании "
        "раздела select в запросе (поле query)"
    )
    @allure.title(
        "В select узла чтения указать 1 поле из таблицы, маппинг произвести на 2 поля, проверить, что валидация "
        "вернула ошибку"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue(url="DEV-23414")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value),
         VariableParams(varName="str_var", varType="in", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node_query_attribute_exists(self, super_user, create_db_all_tables_and_scheme,
                                                                  provider_constructor, diagram_constructor):
        diagram_param_int: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        diagram_param_str: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["str_var"]
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        temp_version_id = diagram_constructor["temp_version_id"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        column_name_int = get_db_column_name(db_table, diagram_param_int)
        column_name_str = get_db_column_name(db_table, diagram_param_str)
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param_int.parameterName,
                                               type_id="1",
                                               node_variable=column_name_int,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param_int.parameterId)
            output_var_mapping2 = read_variable(is_arr=False,
                                                is_compl=False,
                                                is_dict=False,
                                                var_name=diagram_param_str.parameterName,
                                                type_id="2",
                                                node_variable=column_name_str,
                                                is_jdbc_arr_key=False,
                                                param_id=diagram_param_str.parameterId)
            mapping_raw = output_var_mapping2.rowKey
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=f"select {column_name_int}" + " \n" + f"from {table_name}",
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping, output_var_mapping2],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=node_read.nodeId,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение узла чтения данных"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step(
                "Проверка, что валидация возвращает ошибку из-за отсутствия столбца таблицы в поле query,"
                "и узел невалиден"):
            assert \
                validation_response.validationPayload["nodeValidationMap"]["outputVariablesMapping"][mapping_raw][
                    "nodeVariable"] \
                == "Элемент должен фигурировать в описании раздела select в запросе (поле query)" \
                and not node_view.validFlag

    @allure.story(
        "Предусмотрена валидация запроса - проверка корректности полного выражения из поля query"
    )
    @allure.title(
        "В запросе указать where до from"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.smoke
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node_incorrect_query(self, super_user, diagram_read_2):
        node_read: NodeViewShortInfo = diagram_read_2["node_read"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_read_2["param"]
        temp_version_id = diagram_read_2["temp_version_id"]
        provider: DataProviderGetFullView = diagram_read_2["data_provider"]
        db_table = diagram_read_2["db_table"]
        table_name = db_table.name
        column_name = get_db_column_name(db_table, diagram_param)
        sql_query = f"select {column_name}" + " \n" + f"where {column_name}=20" + " \n" + f"from {table_name}"
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id="1",
                                               node_variable=column_name,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=sql_query,
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение узла чтения данных"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step("Формирование body для валидации sql-выражения"):
            sql_validation_construct = SqlValidationApiDto.construct(validationType="NODE",
                                                                     dataProviderUuid=provider.sourceId,
                                                                     sqlSelectQuery=sql_query,
                                                                     nodeId=node_read.nodeId,
                                                                     diagramVersionId=temp_version_id)
        with allure.step(
                "Проверка, что валидация sql-выражения возвращает ошибку синтаксиса, и узел невалидный"):
            with pytest.raises(HTTPError) as e:
                with allure.step("Валидация sql-выражения"):
                    sql_validation_query(super_user, sql_validation_construct)
            sql_validation_response = e.value.response.json()
            assert sql_validation_response["httpCode"] == 422 \
                   and "Ошибка в запросе - ERROR: syntax error" in sql_validation_response["message"] \
                   and not node_view.validFlag

    @allure.story(
        "Нет ошибок, если узел корректно заполнен"
    )
    @allure.title(
        "Обновить узел чтения, добавить валидный источник данных, провести маппинг на переменную"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.postgres
    @pytest.mark.skip("obsolete")
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.smoke
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node_mapping(self, super_user, diagram_read_2):
        node_read: NodeViewShortInfo = diagram_read_2["node_read"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_read_2["param"]
        temp_version_id = diagram_read_2["temp_version_id"]
        diagram_id = diagram_read_2["diagram_id"]
        columns: list[ColumnsDto] = diagram_read_2["table_columns"]
        provider: DataProviderGetFullView = diagram_read_2["data_provider"]
        table_name = diagram_read_2["table_name"]
        column_name = ""
        for column in columns:
            if column.dataType == "integer":
                column_name = column.columnName

        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id=1,
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
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Валидируем узел"):
            validate = validate_diagram(super_user, temp_version_id)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert validate.body["httpCode"] == 200 and validate.body["operation"] == "validate"

    @allure.story(
        "Предусмотрена проверка на соответствие указанных элементов актуальным данным диаграммы "
        "(таблица diagram_in_out_parameter, parameter_type = 'IN' или 'IN_OUT') в случае,"
        " если в запросе (поле query) фигурируют элементы диаграммы"
    )
    @allure.title(
        "В условии where sql-запроса в узле чтения данных указать переменную диаграммы, затем удалить эту переменную, "
        "проверить, что валидация sql-запроса вернула ошибку, и узел невалидный")
    @pytest.mark.scenario("DEV-6398")
    @allure.issue(url="DEV-9663")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value),
         VariableParams(varName="str_var", varType="in", varDataType=IntValueType.str.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node_query_deleted_var(self, super_user, create_db_all_tables_and_scheme,
                                                             provider_constructor, diagram_constructor):
        diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        diagram_param2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["str_var"]
        diagram_exec_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["diagram_execute_status"]
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        temp_version_id = diagram_constructor["temp_version_id"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]

        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        column_name_int = get_db_column_name(db_table, diagram_param)
        column_name_str = get_db_column_name(db_table, diagram_param)
        sql_query = f"select {column_name_int} from {table_name} where {column_name_str} = ${{{diagram_param2.parameterName}}}"
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id="1",
                                               node_variable=column_name_int,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=sql_query,
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Удаление переменной, указанной в условии where"):
            update_diagram_parameters(super_user, str(temp_version_id), [diagram_exec_var,
                                                                         diagram_param])

        with allure.step("Формирование body для валидации sql-выражения"):
            sql_validation_construct = SqlValidationApiDto.construct(validationType="NODE",
                                                                     dataProviderUuid=provider.sourceId,
                                                                     sqlSelectQuery=sql_query,
                                                                     nodeId=node_read.nodeId,
                                                                     diagramVersionId=temp_version_id)
        with allure.step("Валидация узла чтения данных"):
            node_validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                                node_id=node_read.nodeId,
                                                                                body=NodeValidateDto.construct(
                                                                                    nodeTypeId=update_body.nodeTypeId,
                                                                                    properties=update_body.properties)).body)

        with allure.step(
                "Проверка, что валидация sql-выражения возвращает ошибку, и узел невалидный"):
            with pytest.raises(HTTPError) as e:
                with allure.step("Валидация sql-выражения"):
                    sql_validation_query(super_user, sql_validation_construct)
            sql_validation_response = e.value.response.json()
            assert sql_validation_response["httpCode"] == 422 \
                   and sql_validation_response[
                       "message"] == f"Переменная - {diagram_param2.parameterName}, не найдена в данных диаграммы" \
                   and node_validation_response.httpCode == 422 and node_validation_response.validationPayload[
                       "nodeValidationMap"]["query"] == f"Переменная - {diagram_param2.parameterName}, " \
                                                        f"не найдена в данных диаграммы"

    @allure.story("Предусмотренна проверка что переменные учавствующие в запросе были предрасчитанны")
    @allure.title(
        "Обновить узел чтения добавив к нему валидный источник данных и указать 1 поле из таблицы,в запросе "
        "использовать выходную переменную, произвести  маппинг на сквозную переменную"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue(url="DEV-10466")
    @pytest.mark.postgres
    @pytest.mark.smoke
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value),
         VariableParams(varName="out_var", varType="out", varDataType=IntValueType.str.value, isConst=True)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node_query_precalculated_var(self, super_user, create_db_all_tables_and_scheme,
                                                                   provider_constructor, diagram_constructor):
        diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        diagram_param2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_var"]
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        temp_version_id = diagram_constructor["temp_version_id"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        column_name_int = get_db_column_name(db_table, diagram_param)
        column_name_str = get_db_column_name(db_table, diagram_param2)

        sql_query = f"select {column_name_int}" + " \n" + f"from {table_name}" + " \n" + f"where {column_name_str}=${{{diagram_param2.parameterName}}}"
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id="1",
                                               node_variable=column_name_int,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=sql_query,
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
        with allure.step("Формирование body для валидации sql-выражения"):
            sql_validation_construct = SqlValidationApiDto.construct(validationType="NODE",
                                                                     dataProviderUuid=provider.sourceId,
                                                                     sqlSelectQuery=sql_query,
                                                                     nodeId=node_read.nodeId,
                                                                     diagramVersionId=temp_version_id)
        with allure.step("Валидация узла чтения данных"):
            node_validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                                node_id=node_read.nodeId,
                                                                                body=NodeValidateDto.construct(
                                                                                    nodeTypeId=update_body.nodeTypeId,
                                                                                    properties=update_body.properties)).body)
        with allure.step(
                "Проверка, что валидация sql-выражения возвращает ошибку, и узел невалидный"):
            with pytest.raises(HTTPError) as e:
                with allure.step("Валидация sql-выражения"):
                    sql_validation_query(super_user, sql_validation_construct)
            sql_validation_response = e.value.response.json()
            assert sql_validation_response["httpCode"] == 422 \
                   and sql_validation_response[
                       "message"] == f"Переменная - {diagram_param2.parameterName}, не найдена в данных диаграммы" \
                   and node_validation_response.httpCode == 422 and node_validation_response.validationPayload[
                       "nodeValidationMap"]["query"] == f"Переменная - {diagram_param2.parameterName}, " \
                                                        f"не найдена в данных диаграммы"

    @allure.story(
        "Предусмотрена проверка, что указанный в узле источник данных, существует"
    )
    @allure.title(
        "В поле источник данных указать несуществующий источник данных"
    )
    @pytest.mark.scenario("DEV-19559")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_node_non_existent_data_source(self, super_user, diagram_read_2):
        node_read: NodeViewShortInfo = diagram_read_2["node_read"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_read_2["param"]
        temp_version_id = diagram_read_2["temp_version_id"]
        db_table = diagram_read_2["db_table"]
        table_name = db_table.name
        column_name = get_db_column_name(db_table, diagram_param)
        provider_new_id = str(uuid.uuid4())
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id=1,
                                               node_variable=column_name,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            node_read_properties = read_properties(data_provider_uuid=provider_new_id,
                                                   query=f"select {column_name}" + " \n" + f"from {table_name}",
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                           node_id=node_read.nodeId,
                                                                           body=NodeValidateDto.construct(
                                                                               nodeTypeId=update_body.nodeTypeId,
                                                                               properties=update_body.properties)).body)
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение узла чтения данных"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step("Проверка, что валидация возвращает ошибку из-за отсутствия источника с указанным id, "
                         "и узел невалиден"):
            assert \
                validation_response.validationPayload["nodeValidationMap"]["dataProviderUuid"] == \
                f"Источника данных с идентификатором - {provider_new_id} не найдено" \
                and not node_view.validFlag

    @allure.story(
        "Предусмотрена проверка, что указанная в запросе таблица, существует в источнике данных"
    )
    @allure.title(
        "В sql-запросе после from указать несуществующую в источнике данных таблицу"
    )
    @pytest.mark.scenario("DEV-19559")
    @allure.issue(url="DEV-24221")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    def test_create_diagram_with_read_random_table(self, super_user, create_db_all_tables_and_scheme,
                                                   provider_constructor, diagram_constructor):
        diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        temp_version_id = diagram_constructor["temp_version_id"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        random_table_name = generate_string(5).lower()
        column_name_int = get_db_column_name(db_table, diagram_param)

        sql_query = f"select {column_name_int}" + " \n" + f"from {random_table_name}"
        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id="1",
                                               node_variable=column_name_int,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=sql_query,
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
        with allure.step("Валидация узла чтения данных"):
            node_validation_response: ResponseDto = ResponseDto(**validate_node(super_user,
                                                                                node_id=node_read.nodeId,
                                                                                body=NodeValidateDto.construct(
                                                                                    nodeTypeId=update_body.nodeTypeId,
                                                                                    properties=update_body.properties)).body)
        with allure.step("Формирование body для валидации sql-выражения"):
            sql_validation_construct = SqlValidationApiDto.construct(validationType="NODE",
                                                                     dataProviderUuid=provider.sourceId,
                                                                     sqlSelectQuery=sql_query,
                                                                     nodeId=node_read.nodeId,
                                                                     diagramVersionId=temp_version_id)
        with allure.step(
                "Проверка, что валидация sql-выражения возвращает ошибку, и узел невалидный"):
            with pytest.raises(HTTPError) as e:
                with allure.step("Валидация sql-выражения"):
                    sql_validation_query(super_user, sql_validation_construct)
            sql_validation_response = e.value.response.json()
            assert sql_validation_response["httpCode"] == 422 \
                   and f"Ошибка в запросе - ERROR: relation \"{random_table_name}\" does not exist" in \
                   sql_validation_response["message"] \
                   and f"Ошибка в запросе - ERROR: relation \"{random_table_name}\" does not exist" in \
                   node_validation_response.validationPayload["nodeValidationMap"]["query"] \
                   and node_validation_response.httpCode == 422

    @allure.story("Возможно успешно получить узел при наличии функции и закомментированном from")
    @allure.title("В части select указать функцию прокомментировать запрос в части from, сохранить и попытаться "
                  "получить узел")
    @allure.issue('DEV-16055')
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.scenario("DEV-15449")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int),
                                VariableParams(varName="out_str", varType="out", varDataType=IntValueType.str,
                                               isConst=True)])
    @pytest.mark.nodes(["чтение"])
    @pytest.mark.smoke
    def test_create_diagram_with_read_node_commented_from(self, super_user, diagram_constructor,
                                                          create_db_all_tables_and_scheme, provider_constructor):
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_str"]
        temp_version_id = diagram_constructor["temp_version_id"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]

        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        column_name = get_db_column_name(db_table, diagram_param)

        with allure.step("Обновление узла чтения"):
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name=diagram_param.parameterName,
                                               type_id=diagram_param.typeId,
                                               node_variable=column_name,
                                               is_jdbc_arr_key=False,
                                               param_id=diagram_param.parameterId)
            node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                                   query=f"select TO_CHAR(now(), 'yyyy-mm-ddThh24:mi:ss.MS') AS {column_name}" +
                                                         " \n" + f"--from {table_name}",
                                                   allow_multi_result_response=False,
                                                   out_mapping_vars=[output_var_mapping],
                                                   selected_table_names=[table_name])
            update_body = read_node_construct(x=700, y=202.22915649414062,
                                              temp_version_id=temp_version_id,
                                              properties=node_read_properties,
                                              operation="update")
            update_node(super_user, node_id=node_read.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получаем узел"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step("Проверка, что узел получен, и он валидный"):
            assert node_view.validFlag

    @allure.story("Для колонки БД возвращается корректный тип, доступный для маппинга")
    @allure.title("Создать узел чтения данных с таблицей со всеми стандартными типами, проверить, что для каждого "
                  "поля таблицы вернулся корректный тип")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.scenario("DEV-15449")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение"])
    @pytest.mark.smoke
    def test_create_diagram_with_read_node_correct_types(self, super_user, diagram_constructor,
                                                         create_db_all_tables_and_scheme, provider_constructor):
        node_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        temp_version_id = diagram_constructor["temp_version_id"]
        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = db_table.name
        columns = provider_constructor["columns"]
        read_mapping = []
        for column in columns:
            output_var_mapping = read_variable(is_arr=False,
                                               is_compl=False,
                                               is_dict=False,
                                               var_name="",
                                               type_id="",
                                               node_variable=column.columnName,
                                               is_jdbc_arr_key=False)
            read_mapping.append(output_var_mapping)
        node_read_properties = read_properties(data_provider_uuid=provider.sourceId,
                                               query=f"select {columns[0].columnName}, "
                                                     f"{columns[1].columnName}, "
                                                     f"{columns[2].columnName}, "
                                                     f"{columns[3].columnName},"
                                                     f"{columns[4].columnName}, "
                                                     f"{columns[5].columnName}, "
                                                     f"{columns[6].columnName}, "
                                                     f"{columns[7].columnName} "
                                                     f"from {table_name}",
                                               allow_multi_result_response=False,
                                               out_mapping_vars=read_mapping,
                                               selected_table_names=[table_name])
        update_body = read_node_construct(x=700, y=202.22915649414062,
                                          temp_version_id=temp_version_id,
                                          properties=node_read_properties,
                                          operation="update")
        update_node(super_user, node_id=node_read.nodeId, body=update_body,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=update_body.nodeTypeId,
                        properties=update_body.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_read.nodeId).body
            )
        with allure.step("Проверка, что для каждого поля таблицы возвращается корректный тип переменной диаграммы"):
            with allure.step(
                    "Формирование body для получения типа переменной диаграммы, подходящей для маппинга для текущей "
                    "колонки"):
                for out_var_map in node_view.properties["outputVariablesMapping"]:
                    types_by_column_construct = AvailableTypesRequestDto.construct(sourceId=provider.sourceId,
                                                                                   typesRetrieveType="QUERY",
                                                                                   query=f"select {columns[0].columnName}, "
                                                                                         f"{columns[1].columnName}, "
                                                                                         f"{columns[2].columnName}, "
                                                                                         f"{columns[3].columnName},"
                                                                                         f"{columns[4].columnName}, "
                                                                                         f"{columns[5].columnName}, "
                                                                                         f"{columns[6].columnName}, "
                                                                                         f"{columns[7].columnName} "
                                                                                         f"from {table_name}",
                                                                                   columnName=out_var_map[
                                                                                       "nodeVariable"])
                    with allure.step("Получение вернувшегося типа"):
                        diagram_type = post_data_provider_types_by_column(super_user, types_by_column_construct).body

                    with allure.step("Получение имени колонки, которой соответствует вернувшийся тип"):
                        cur_attr_db_column_name = get_db_column_name(db_table, type_id=diagram_type[0])
                    assert cur_attr_db_column_name == out_var_map["nodeVariable"]

    @allure.story(
        "Можно получить тип, доступный для маппинга на колонку, если в запросе не указано название таблицы")
    @allure.title("Создать узел чтения данных, указать запрос без указания таблицы, проверить, что вернулся "
                  "корректный тип")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.scenario("DEV-15449")
    @pytest.mark.smoke
    def test_create_diagram_with_read_node_correct_types2(self, super_user, provider_constructor):
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        with allure.step(
                "Формирование body для получения типа переменной диаграммы, подходящей для маппинга"):
            types_by_column_construct = AvailableTypesRequestDto.construct(sourceId=provider.sourceId,
                                                                           typesRetrieveType="QUERY",
                                                                           query=f"select 1::int AS column_name",
                                                                           columnName="column_name")
        with allure.step("Получение типа, соответствующего колонке"):
            diagram_type = post_data_provider_types_by_column(super_user, types_by_column_construct).body
        with allure.step(
                "Проверка, что для указанного в запросе типа int вернулся корректный тип переменной диаграммы"):
            assert IntValueType.int.value == diagram_type[0]

    @allure.story(
        "Можно получить тип, доступный для маппинга на колонку, если в запросе есть точка с запятой")
    @allure.title("Создать узел чтения данных, указать запрос с точкой запятой в конце, проверить, что вернулся "
                  "корректный тип")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.scenario("DEV-15449")
    @pytest.mark.smoke
    def test_create_diagram_with_read_node_correct_types2(self, super_user, provider_constructor,
                                                          create_db_all_tables_and_scheme):
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        db_table = create_db_all_tables_and_scheme["read_node_table"]
        table_name = create_db_all_tables_and_scheme["read_node_table"].name
        columns = provider_constructor["columns"]
        column_name = columns[0].columnName
        with allure.step(
                "Формирование body для получения типа переменной диаграммы, подходящей для маппинга"):
            types_by_column_construct = AvailableTypesRequestDto.construct(sourceId=provider.sourceId,
                                                                           typesRetrieveType="QUERY",
                                                                           query=f"select {column_name} "
                                                                                 f"from {table_name}",
                                                                           columnName=column_name)
        with allure.step("Получение типа, соответствующего колонке"):
            diagram_type = post_data_provider_types_by_column(super_user, types_by_column_construct).body
        with allure.step("Получение имени колонки, которой соответствует вернувшийся тип"):
            db_column_name = get_db_column_name(db_table, type_id=diagram_type[0])
        with allure.step(
                "Проверка, что для указанной колонки вернулся корректный тип переменной диаграммы"):
            assert db_column_name == column_name
