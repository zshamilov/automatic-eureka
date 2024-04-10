import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import NodeViewWithVariablesDto, NodeUpdateDto, DiagramInOutParameterFullViewDto, \
    NodeRemapDto, Properties, NodeAutoMappingResponseDto, Finish
from products.Decision.framework.steps.decision_steps_nodes import get_node_by_id, automap_node, update_node, remap_node
from products.Decision.utilities.custom_models import VariableParams, IntValueType, IntNodeType


@allure.epic("Диаграммы")
@allure.feature("Автомаппинг")
@pytest.mark.scenario("DEV-21773")
class TestAutomap:
    @allure.story("При обновлении узла завершения ответом из автомаппинга - узел валиден")
    @allure.title("Создать диаграмму со сквозной переменной, вызвать автомаппинг для узла завершения, обновить узел"
                  "завершения ответом из автомаппинга, проверить, что узел валиден")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=False)])
    @pytest.mark.smoke
    def test_automap_node_finish_is_valid(self, super_user, diagram_constructor):
        with allure.step("Получение идентификатор диаграммы и узла заверешнения"):
            end_node_id = diagram_constructor["node_end_id"]
            temp_version_id = diagram_constructor["temp_version_id"]
            end_node_view = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, end_node_id).body)
        with allure.step("Вызов автомаппинга и получение имен и идентификаторов переменных из маппинга"):
            automap_result = automap_node(super_user, end_node_id, "mappingVariables").body

            end_node_view.properties["mappingVariables"] = automap_result["mappingVariables"]
            update_body = NodeUpdateDto.construct(**end_node_view.dict(), diagramVersionId=temp_version_id)
            update_node(super_user, node_id=end_node_id, body=update_body)
            updated_end_node_view = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, end_node_id).body)
        with allure.step("Проверка, что узел, после обновления ответом из автомапа - валиден"):
            assert updated_end_node_view.validFlag

    @allure.story(
        "При вызове автомаппинга для узла завершения в ответе возвращается корректное имя и идентификатор переменной "
        "маппинга")
    @allure.title("Создать диаграмму со сквозной переменной, вызвать автомаппинг для узла завершения, убедиться, что "
                  "пришли корректные имена и идентификаторы переменных")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=False)])
    @pytest.mark.smoke
    def test_automap_node_finish_returns_end_variables(self, super_user, diagram_constructor):
        with allure.step("Получение идентификатор диаграммы и узла заверешнения"):
            end_node_id = diagram_constructor["node_end_id"]
            temp_version_id = diagram_constructor["temp_version_id"]
            end_node_view = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, end_node_id).body)
        with allure.step("Вызов автомаппинга и получение имен и идентификаторов переменных из маппинга"):
            automap_result = automap_node(super_user, end_node_id, "mappingVariables").body
            end_node_view.properties["mappingVariables"] = automap_result["mappingVariables"]
        with allure.step("Апдейт узла завершения с данными полученными из автомаппинга"):
            node_end_update_body = NodeUpdateDto.construct(**end_node_view.dict(), diagramVersionId=temp_version_id)
            update_node(super_user, node_id=end_node_id, body=node_end_update_body)
            end_node_variables_info = end_node_view.properties["mappingVariables"]
            automap_mapping_variables_info = automap_result["mappingVariables"]
            automap_id_mapping_var = automap_mapping_variables_info[0]["id"]
            automap_name_mapping_var = automap_mapping_variables_info[0]["variableName"]
            automap_id_parameter = automap_mapping_variables_info[0]["parameter"]["parameterId"]
            automap_name_parameter = automap_mapping_variables_info[0]["parameter"]["parameterName"]
            node_id_parameter = end_node_variables_info[0]["parameter"]["parameterId"]
            node_name_parameter = end_node_variables_info[0]["parameter"]["parameterName"]
        with allure.step("Имена и идентификаторы возвращенных автомаппингом параметров "
                         "соответствуют выходным переменным в узле"):
            assert node_id_parameter == automap_id_parameter == automap_id_mapping_var
            assert node_name_parameter == automap_name_parameter == automap_name_mapping_var

    @allure.story("При вызове автомаппинга для узла завершения в ответе НЕ возвращается не расчитанная переменная")
    @allure.title("Создать диаграмму со сквозной и выходной переменной, вызвать автомаппинг для узла завершения, "
                  "убедиться, что выходная переменная не вернулась из автомаппинга")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=False),
         VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value, isConst=False)])
    @pytest.mark.smoke
    def test_automap_node_finish_not_returns_uncalculated(self, super_user, diagram_constructor):
        with allure.step("Получение идентификатор диаграммы и узла заверешнения"):
            is_not_calculated_param_absent = True
            end_node_id = diagram_constructor["node_end_id"]
        with allure.step("Вызов автомаппинга и получение имен и идентификаторов переменных из маппинга"):
            automap_result = Finish(**automap_node(super_user, end_node_id, "mappingVariables").body)

            for el in automap_result.mappingVariables:
                if el.variableName == "out_int":
                    is_not_calculated_param_absent = False
                    break

        with allure.step("Проверка, что нерасчитанный параметр отсутствует"):
            assert is_not_calculated_param_absent

    @allure.story("При вызове автомаппинга для узла завершения, в котором задана константа для сквозной"
                  "переменной, в ответе возвращается конфликт для замапленной переменной")
    @allure.title("Создать диаграмму со сквозной и выходной переменной, вызвать автомаппинг для узла завершения, "
                  "убедиться, что замапленная переменная в списке конфликтов")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=True)])
    @pytest.mark.smoke
    def test_automap_node_finish_returns_conflict_var(self, super_user, diagram_constructor):
        with allure.step("Получение идентификатор диаграммы и узла заверешнения"):
            end_node_id = diagram_constructor["node_end_id"]
            end_node_view = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, end_node_id).body)
            end_node_variables_info = end_node_view.properties["mappingVariables"]
            node_id_parameter = end_node_variables_info[0]["parameter"]["parameterId"]
            node_name_parameter = end_node_variables_info[0]["parameter"]["parameterName"]
            node_name_mapping = end_node_variables_info[0]["variableName"]
        with allure.step("Вызов автомаппинга и получение конфликтующих переменных"):
            with pytest.raises(HTTPError, match='422') as e:
                automap_node(super_user, end_node_id, "mappingVariables")
            response = NodeAutoMappingResponseDto(**e.value.response.json())
            automap_conflicts = response.autoMappingConflicts
            automap_current_var_value = automap_conflicts[0].currentVariableValue
            automap_variable_id = automap_conflicts[0].variableId
            automap_suggested_var_val = automap_conflicts[0].suggestedVariableValue
            automap_var_name = automap_conflicts[0].variableName
        with allure.step("Проверка, что идентификатор, имя и текущее значение корректно"):
            assert len(response.autoMappingConflicts) == 1 \
                   and automap_suggested_var_val == automap_var_name == node_name_parameter \
                   and automap_variable_id == node_id_parameter \
                   and automap_current_var_value == node_name_mapping

    @allure.story("При вызове автомаппинга для узла завершения, в котором задана константа для сквозной"
                  "переменной, после повторного вызова автомаппинга с принудительным автомапом для переменной приходит "
                  "корректный маппинг ")
    @allure.title(
        "Создать диаграмму со сквозной и выходной переменной, вызвать автомаппинг для узла завершения, вызвать"
        "автомаппинг повторно, передав конфликтную переменную, проверить, что вернулся корректный маппинг")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=True)])
    @pytest.mark.smoke
    def test_automap_node_finish_returns_force_automap(self, super_user, diagram_constructor):
        with allure.step("Получение идентификатор диаграммы и узла заверешнения"):
            end_node_id = diagram_constructor["node_end_id"]
            end_node_view = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, end_node_id).body)
        with allure.step("Вызов автомаппинга и получение имен и идентификаторов переменных из маппинга с конфликтами"):
            with pytest.raises(HTTPError, match="422") as e:
                automap_node(super_user, end_node_id, "mappingVariables")
            response = NodeAutoMappingResponseDto(**e.value.response.json())
            id_for_force = response.autoMappingConflicts[0].variableId
        with allure.step("Вызов автомаппинга с указанием принудительной для автомаппинга переменной"):
            automap_force_result = Finish(**automap_node(super_user, end_node_id, "mappingVariables",
                                                         force_automap_ids=[id_for_force]).body)
            end_node_variables_info = end_node_view.properties["mappingVariables"]
            automap_mapping_variables_info = automap_force_result.mappingVariables
            automap_id_mapping_var = automap_mapping_variables_info[0].id
            automap_name_mapping_var = automap_mapping_variables_info[0].variableName
            automap_id_parameter = automap_mapping_variables_info[0].parameter.parameterId
            automap_name_parameter = automap_mapping_variables_info[0].parameter.parameterName
            node_id_parameter = end_node_variables_info[0]["parameter"]["parameterId"]
            node_name_parameter = end_node_variables_info[0]["parameter"]["parameterName"]
        with allure.step("Проверка, что имена и идентификаторы возвращенных автомаппингом параметров "
                         "соответствуют изначальным идентификаторам узла"):
            assert node_id_parameter == automap_id_parameter == automap_id_mapping_var
            assert node_name_parameter == automap_name_parameter == automap_name_mapping_var

    @allure.story("При вызове автомаппинга для узла завершения, в котором задана константа для сквозной"
                  "переменной, после повторного вызова автомаппинга с игнорированием переменной, игнорируемая "
                  "переменная не возвращается")
    @allure.title(
        "Создать диаграмму со сквозной и выходной переменной, вызвать автомаппинг для узла завершения, вызвать"
        "автомаппинг повторно, передав конфликтную переменную, проверить, что вернулся корректный маппинг")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=True),
         VariableParams(varName="in_out_int1", varType="in_out", varDataType=IntValueType.int.value, isConst=False)
         ])
    @pytest.mark.smoke
    def test_automap_node_finish_not_returns_skip_param(self, super_user, diagram_constructor):
        with allure.step("Получение идентификатор диаграммы и узла заверешнения"):
            is_skipped_param_absent = True
            end_node_id = diagram_constructor["node_end_id"]
        with allure.step("Вызов автомаппинга и получение имен и идентификаторов переменных из маппинга с конфликтами"):
            with pytest.raises(HTTPError, match='422') as e:
                automap_node(super_user, end_node_id, "mappingVariables")
            response = NodeAutoMappingResponseDto(**e.value.response.json())
            id_for_skip = response.autoMappingConflicts[0].variableId
        with allure.step("Вызов автомаппинга с указанием идентификатора игнорируемой переменной"):
            automap_skip_result = Finish(**automap_node(super_user, end_node_id, "mappingVariables",
                                                        skip_automap_ids=[id_for_skip]).body)
            automap_skip_result_variables = automap_skip_result.mappingVariables
            for el in automap_skip_result_variables:
                if el.id == id_for_skip:
                    is_skipped_param_absent = False
                    break
        with allure.step("проверка, что игнорируемой переменной нет в результате автомаппинга"):
            assert is_skipped_param_absent and len(automap_skip_result_variables) == 2

    @allure.story(
        "При вызове автомаппинга для узла завершения в ответе возвращается корректное имя и идентификатор переменной "
        "маппинга")
    @allure.title("Создать диаграмму со сквозной переменной, вызвать автомаппинг для узла завершения, убедиться, что "
                  "пришли корректные имена и идентификаторы переменных")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="in_out_int")])
    @pytest.mark.smoke
    def test_automap_node_finish_returns_nothing_if_mapping_exists(self, super_user, diagram_constructor):
        with allure.step("Получение идентификатор диаграммы и узла заверешнения"):
            end_node_id = diagram_constructor["node_end_id"]
        with allure.step("Вызов автомаппинга и получение имен и идентификаторов переменных из маппинга"):
            automap_result = automap_node(super_user, end_node_id, "mappingVariables")
            automap_body = automap_result.body
            automap_code = automap_result.status
        with allure.step("Проверка, что автомаппинг ничего не вернул"):
            assert automap_body == {} and automap_code == 204

    @allure.story(
        "Автомаппинг во входных и выходных переменных узла поддиаграммы"
    )
    @allure.title(
        "В узел внешнего сервиса добавить внешний сервис проверить validFlag"
    )
    @pytest.mark.smoke
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var_name", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="in_out")])
    @pytest.mark.nodes(["поддиаграмма"])
    def test_automap_node_subdiagram_is_valid(self, super_user, diagram_constructor, simple_diagram):
        subdiagram_version_id = simple_diagram["create_result"]["uuid"]
        subdiagram_id = simple_diagram["template"]["diagramId"]
        temp_version_id = diagram_constructor["temp_version_id"]
        node_sub_id = diagram_constructor["nodes"]["поддиаграмма"].nodeId
        diagra_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var_name"]
        with allure.step("Получение информации об узле поддиаграммы"):
            sub_node = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, node_sub_id).body)
        with allure.step("Ремап на переменные поддиаграммы"):
            sub_node.properties = remap_node(super_user,
                                             node_sub_id,
                                             NodeRemapDto.construct(
                                                 properties=Properties.construct(subdiagramId="",
                                                                                 versionId="",
                                                                                 inputVariablesMapping=[],
                                                                                 outputVariablesMapping=[]),
                                                 objectVersionId=subdiagram_version_id,
                                                 objectId=subdiagram_id,
                                                 nodeTypeId=IntNodeType.subdiagram.value)).body
        with allure.step("Апдейт узла поддиаграммы на незаполненные переменные поддиаграммы"):
            upd_body = NodeUpdateDto.construct(**sub_node.dict(), diagramVersionId=temp_version_id)
            update_node(super_user, node_id=node_sub_id, body=upd_body)
        with allure.step("Получение информации об узле поддиаграммы"):
            sub_node = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user, node_sub_id).body)
        with allure.step("Автомаппинг входных переменных узла поддиаграммы на переменную диаграммы"):
            automap_result_for_output = automap_node(super_user,
                                                     node_sub_id,
                                                     "outputVariablesMapping").body["outputVariablesMapping"]
        with allure.step("Автомаппинг выходных переменных узла поддиаграммы на переменную диаграммы"):
            automap_result_for_input = automap_node(super_user,
                                                    node_sub_id,
                                                    "inputVariablesMapping").body["inputVariablesMapping"]
            sub_node.properties["inputVariablesMapping"] = automap_result_for_input
            sub_node.properties["outputVariablesMapping"] = automap_result_for_output
        with allure.step("Апдейт узла с данными взятыми из автомаппинга"):
            upd_body = NodeUpdateDto.construct(**sub_node.dict(), diagramVersionId=temp_version_id)
            update_node(super_user,
                        node_id=node_sub_id,
                        body=upd_body)
        with allure.step("Получение информации об узле поддиаграммы"):
            sub_node_info = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                                node_sub_id).body)
        with allure.step("Узел валиден, на вход и выход намаплена сквозная переменная диаграмма"):
            assert sub_node_info.validFlag
            assert sub_node_info.properties["inputVariablesMapping"][0]["id"] == diagra_var.parameterId
            assert any(var["id"] == diagra_var.parameterId for var in sub_node_info.properties["outputVariablesMapping"])
