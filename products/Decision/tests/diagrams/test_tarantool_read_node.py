import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, DiagramViewDto, NodeViewShortInfo, SearchType, \
    NodeValidateDto, NodeViewWithVariablesDto, FunctionsDto, LuaResultType, DiagramInOutParameterFullViewDto, Predicate
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import create_node, delete_node_by_id, get_node_by_id, \
    update_node
from products.Decision.utilities.custom_models import IntNodeType, VariableParams, IntValueType
from products.Decision.utilities.node_cunstructors import empty_node_construct, \
    tarantool_read_input_var, read_variable, tarantool_read_index_var
from products.Decision.utilities.tarantool_node_constructos import tarantool_read_construct


@allure.epic("Диаграммы")
@allure.feature("Узел чтение Tarantool")
@pytest.mark.scenario("DEV-8462")
class TestDiagramsTarantoolReadNode:
    @allure.story("Узел чтение Tarantool создаётся")
    @allure.title(
        "Создать диаграмму с узлом чтение Tarantool без параметров, увидеть, что создался"
    )
    @pytest.mark.smoke
    def test_create_tarantool_read_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла чтение Tarantool"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.tarantoolRead,
                                             diagram_version_id=temp_version_id,
                                             node_name="Чтение Tarantool")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла корректен и равен чтение Tarantool"
        ):
            assert diagram.nodes[str(node_id)].nodeTypeId == IntNodeType.tarantoolRead

    @allure.story("Узел чтение Tarantool удаляется")
    @allure.title(
        "Создать диаграмму с узлом чтение Tarantool без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.smoke
    def test_delete_node_tarantool_read(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла чтение Tarantool"):
            node_body = empty_node_construct(x=100, y=400,
                                             node_type=IntNodeType.tarantoolRead,
                                             diagram_version_id=temp_version_id,
                                             node_name="Чтение Tarantool")
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_id).status == 404

    @allure.story(
        "Можно создать узел чтение Tarantool с типом поиск по индексу и настроить его"
    )
    @allure.title(
        "Обновить узел чтение Tarantool, выбрав тип блока поиск по индексу и настроив его"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("ALL")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_long", varType="out", varDataType=IntValueType.long.value),
         VariableParams(varName="out_str", varType="out", varDataType=IntValueType.str.value),
         VariableParams(varName="in_long_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_long_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["чтение тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_read_index_node_valid(self, super_user, diagram_constructor, provider_constructor):
        with allure.step("Получение информации об объектах"):
            node_tarantool_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение тарантул"]
            out_long: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_long"]
            out_str: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_str"]
            in_v1: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_long_1"]
            in_v2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_long_2"]
            provider_info = provider_constructor["provider_info"]
            columns = provider_constructor["columns"]
            searched_index = provider_constructor["index"][0]
            columns_for_inp = []
            columns_for_read = []
        with allure.step("Заполнение узла"):
            for column in columns:
                if column.isPrimary:
                    columns_for_inp.append(column)
                else:
                    columns_for_read.append(column)
            inp_var_1 = tarantool_read_input_var(var_name="in_long_1", type_id=IntValueType.long.value,
                                                 providers_column_name=columns_for_inp[0].columnName,
                                                 providers_column_data_type=columns_for_inp[0].dataType,
                                                 param_id=in_v1.parameterId)
            inp_var_2 = tarantool_read_input_var(var_name="in_long_2", type_id=IntValueType.long.value,
                                                 providers_column_name=columns_for_inp[1].columnName,
                                                 providers_column_data_type=columns_for_inp[1].dataType,
                                                 param_id=in_v2.parameterId)
            index_var = tarantool_read_index_var(index_name=searched_index.indexName,
                                                 predicate=Predicate.EQUALS,
                                                 order=0,
                                                 input_vars_mapping=[inp_var_1, inp_var_2])
            read_var_1 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="out_long",
                                       type_id=IntValueType.long.value, node_variable=columns_for_read[0].columnName,
                                       is_jdbc_arr_key=False, node_variable_type=columns_for_read[0].dataType,
                                       param_id=out_long.parameterId)
            read_var_2 = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name="out_str",
                                       type_id=IntValueType.str.value, node_variable=columns_for_read[1].columnName,
                                       is_jdbc_arr_key=False, node_variable_type=columns_for_read[1].dataType,
                                       param_id=out_str.parameterId)
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
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_read.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert node_view.validFlag

    @allure.story(
        "Можно создать узел чтение Tarantool с типом вызов функции и настроить его"
    )
    @allure.title(
        "Обновить узел чтение Tarantool, выбрав тип блока вызов функции и настроив его"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.search_type("LUA_FUNCTION_SEARCH")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["чтение тарантул"])
    @pytest.mark.smoke
    @pytest.mark.tarantool
    def test_tarantool_read_fun_node_valid(self, super_user, diagram_constructor, provider_constructor):
        with allure.step("Получение информации об объектах"):
            node_tarantool_read: NodeViewShortInfo = diagram_constructor["nodes"]["чтение тарантул"]
            out_v: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int"]
            in_v1: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_1"]
            in_v2: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_2"]
            provider_info = provider_constructor["provider_info"]
            functions = provider_constructor["functions"]
            input_params = []
            function: FunctionsDto
        with allure.step("Заполнение узла"):
            for func in functions:
                if func.name == "get_sum":
                    function = func
            for func in function.arguments:
                input_params.append(func)
            inp_var_1 = tarantool_read_input_var(var_name="in_int_1", type_id=IntValueType.int.value,
                                                 providers_column_name=input_params[0],
                                                 providers_column_data_type=None, is_null=False,
                                                 param_id=in_v1.parameterId)
            inp_var_2 = tarantool_read_input_var(var_name="in_int_2", type_id=IntValueType.int.value,
                                                 providers_column_name=input_params[1],
                                                 providers_column_data_type=None, is_null=False,
                                                 param_id=in_v2.parameterId)
            calc_var = read_variable(is_arr=False, is_compl=False, is_dict=False, var_name=out_v.parameterName,
                                     type_id=IntValueType.int.value, is_jdbc_arr_key=True,
                                     param_id=out_v.parameterId)
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
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_tarantool_read.nodeId).body)
        with allure.step("Проверка, что указанные данные успешно добавились в узел"):
            assert node_view.validFlag
