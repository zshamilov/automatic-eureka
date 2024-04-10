import uuid

import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ScriptFullView, ScriptVariableFullView, NodeViewShortInfo, ScriptType2, \
    NodeViewWithVariablesDto, DiagramParameterDto, DiagramValidateResponseDto, \
    DiagramInOutParameterFullViewDto, ComplexTypeGetFullView, RulesetVariableProperties, BranchNodeBranch, \
    DefaultBranch, NodeValidateDto
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_parameters, update_diagram_parameters
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id, revalidate_node
from products.Decision.utilities.custom_models import IntValueType, VariableParams, AttrInfo, NodeFullInfo, IntNodeType
from products.Decision.utilities.node_cunstructors import variables_for_node, node_update_construct, \
    branch_node_properties, branch_node_construct, ruleset_node_construct
from products.Decision.utilities.variable_constructors import variable_construct
from products.Decision.runtime_tests.runtime_fixtures.var_calc_fixtures import diagram_calc_prim_v
from products.Decision.runtime_tests.runtime_fixtures.branch_fixtures import diagram_branch_saved
from products.Decision.runtime_tests.runtime_fixtures.ruleset_fixtures import diagram_ruleset_saved


@allure.epic("Диаграммы")
@allure.feature("Валидация узлов")
@pytest.mark.scenario("DEV-6398")
class TestDiagramsRevalidateNodes:
    @allure.story("Узел, ставший невалидным, после изменения типа переменной, указанной в нем, возвращается в "
                  "invalidNodeIds и сообщении об ошибке")
    @allure.title("Изменить тип переменной, намапленной на атрибуты кастомного кода, на некорректный, проверить, "
                  "что ревалидация вернула список невалидных узлов и в нем только узел кастомного кода")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="in_out_var")])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_invalid_node_revalidate(self, super_user, diagram_constructor, create_groovy_code_int_vars):
        with allure.step("Получение информации о скрипте"):
            script_view: ScriptFullView = create_groovy_code_int_vars["code_view"]
            script_id = script_view.scriptId
            script_version_id = script_view.versionId
            script_input_var: ScriptVariableFullView = (
                create_groovy_code_int_vars["inp_var"]
            )
            script_output_var: ScriptVariableFullView = (
                create_groovy_code_int_vars["out_var"]
            )
        with allure.step("Обновление узла кастомного кода"):
            node_custom_code: NodeViewShortInfo = diagram_constructor["nodes"]["кастомный код"]
            in_out_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
            inp_var_map_validate = variables_for_node(
                node_type="custom_code",
                type_id=script_input_var.primitiveTypeId,
                is_arr=False,
                is_compl=False,
                name=in_out_variable.parameterName,
                node_variable=script_input_var.variableName,
                outer_variable_id=script_input_var.variableId,
                param_id=in_out_variable.parameterId
            )
            out_var_map_validate = variables_for_node(
                node_type="custom_code",
                type_id=script_output_var.primitiveTypeId,
                is_arr=False,
                is_compl=False,
                name=in_out_variable.parameterName,
                node_variable=script_output_var.variableName,
                outer_variable_id=script_output_var.variableId,
                param_id=in_out_variable.parameterId
            )
            node_script_validate = node_update_construct(
                x=700,
                y=202.22915649414062,
                node_type="custom_code",
                temp_version_id=diagram_constructor["temp_version_id"],
                script_id=script_id,
                script_version_id=script_version_id,
                script_type=ScriptType2.GROOVY,
                inp_custom_code_vars=[inp_var_map_validate],
                out_custom_code_vars=[out_var_map_validate],
            )
            inp_var_map = variables_for_node(
                node_type="custom_code",
                is_arr=False,
                is_compl=False,
                name=in_out_variable.parameterName,
                outer_variable_id=script_input_var.variableId,
                param_id=in_out_variable.parameterId
            )
            out_var_map = variables_for_node(
                node_type="custom_code",
                is_arr=False,
                is_compl=False,
                name=in_out_variable.parameterName,
                outer_variable_id=script_output_var.variableId,
                param_id=in_out_variable.parameterId
            )
            node_script_update = node_update_construct(
                x=700,
                y=202.22915649414062,
                node_type="custom_code",
                temp_version_id=diagram_constructor["temp_version_id"],
                script_id=script_id,
                script_version_id=script_version_id,
                script_type=ScriptType2.GROOVY,
                inp_custom_code_vars=[inp_var_map],
                out_custom_code_vars=[out_var_map],
            )
            update_node(super_user, node_id=node_custom_code.nodeId, body=node_script_update,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_custom_code.nodeTypeId,
                            properties=node_script_validate.properties,
                            addedVariables=[]))
        with allure.step("Изменение типа переменной, использующейся в узле кастомного кода"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            for param in diagram_parameters.inOutParameters:
                if param["parameterName"] == in_out_variable.parameterName:
                    param['typeId'] = '2'
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"],
                                      diagram_parameters.inOutParameters, inner_vars=[])
            with allure.step("Проверка, что ревалидация вернула список невалидных узлов и в нем только узел "
                             "кастомного кода"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, node_custom_code.nodeId).body)
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and node_custom_code.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки."

    @allure.story("Узел, ставший валидным, после изменения типа переменной, указанной в нем, не возвращается в "
                  "invalidNodeIds")
    @allure.title("Изменить тип переменной, намапленной на атрибуты кастомного кода, на корректный, проверить, "
                  "что ревалидация вернула 200")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.str.value, isConst=False,
                        varValue="in_out_var")])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_valid_node_revalidate(self, super_user, diagram_constructor, create_groovy_code_int_vars):
        with allure.step("Получение информации о скрипте"):
            script_view: ScriptFullView = create_groovy_code_int_vars["code_view"]
            script_id = script_view.scriptId
            script_version_id = script_view.versionId
            script_input_var: ScriptVariableFullView = (
                create_groovy_code_int_vars["inp_var"]
            )
            script_output_var: ScriptVariableFullView = (
                create_groovy_code_int_vars["out_var"]
            )
        with allure.step("Обновление узла кастомного кода"):
            node_custom_code: NodeViewShortInfo = diagram_constructor["nodes"]["кастомный код"]
            in_out_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
            inp_var_map_validate = variables_for_node(
                node_type="custom_code",
                type_id=script_input_var.primitiveTypeId,
                is_arr=False,
                is_compl=False,
                name=in_out_variable.parameterName,
                node_variable=script_input_var.variableName,
                outer_variable_id=script_input_var.variableId,
                param_id=in_out_variable.parameterId
            )
            out_var_map_validate = variables_for_node(
                node_type="custom_code",
                type_id=script_output_var.primitiveTypeId,
                is_arr=False,
                is_compl=False,
                name=in_out_variable.parameterName,
                node_variable=script_output_var.variableName,
                outer_variable_id=script_output_var.variableId,
                param_id=in_out_variable.parameterId
            )
            node_script_validate = node_update_construct(
                x=700,
                y=202.22915649414062,
                node_type="custom_code",
                temp_version_id=diagram_constructor["temp_version_id"],
                script_id=script_id,
                script_version_id=script_version_id,
                script_type=ScriptType2.GROOVY,
                inp_custom_code_vars=[inp_var_map_validate],
                out_custom_code_vars=[out_var_map_validate],
            )
            inp_var_map = variables_for_node(
                is_arr=False,
                is_compl=False,
                node_type="custom_code",
                name=in_out_variable.parameterName,
                outer_variable_id=script_input_var.variableId,
                param_id=in_out_variable.parameterId
            )
            out_var_map = variables_for_node(
                is_arr=False,
                is_compl=False,
                node_type="custom_code",
                name=in_out_variable.parameterName,
                outer_variable_id=script_output_var.variableId,
                param_id=in_out_variable.parameterId
            )
            node_script_update = node_update_construct(
                x=700,
                y=202.22915649414062,
                node_type="custom_code",
                temp_version_id=diagram_constructor["temp_version_id"],
                script_id=script_id,
                script_version_id=script_version_id,
                script_type=ScriptType2.GROOVY,
                inp_custom_code_vars=[inp_var_map],
                out_custom_code_vars=[out_var_map],
            )
            update_node(super_user, node_id=node_custom_code.nodeId, body=node_script_update,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_custom_code.nodeTypeId,
                            properties=node_script_validate.properties,
                            addedVariables=[]))
        with allure.step("Изменение типа переменной, использующейся в узле кастомного кода"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            for param in diagram_parameters.inOutParameters:
                if param["parameterName"] == in_out_variable.parameterName:
                    param["typeId"] = '1'
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"],
                                      diagram_parameters.inOutParameters, inner_vars=[])
        with allure.step("Ревалидация узлов"):
            revalidate_node_response = DiagramValidateResponseDto.construct(
                **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
        with allure.step("Проверка, что ревалидация вернула код 200 и узел кастомного кода валидный"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_custom_code.nodeId).body)

            assert revalidate_node_response.httpCode == 200 and node_view.validFlag

    @allure.story("После добавления выходной переменной узел завершения становится невалидным и возвращается в"
                  "invalidNodeIds и сообщении об ошибке")
    @allure.title("Добавить выходную переменную, проверить, что ревалидация вернула список невалидных узлов и в нем "
                  "только узел Завершения")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="in_out_int")])
    @pytest.mark.smoke
    def test_finish_node_revalidate(self, super_user, diagram_constructor):
        finish_node: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
        with allure.step("Добавление выходной переменной"):
            vers_id_out = str(uuid.uuid4())
            out_int_var = variable_construct(array_flag=False,
                                             complex_flag=False,
                                             default_value=None,
                                             is_execute_status=None,
                                             order_num=3,
                                             param_name="out_int_v",
                                             parameter_type="out",
                                             parameter_version_id=vers_id_out,
                                             type_id=1,
                                             parameter_id=vers_id_out)
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            diagram_parameters.inOutParameters.append(out_int_var)
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"],
                                      diagram_parameters.inOutParameters)
            with allure.step(
                    "Проверка, что ревалидация вернула список невалидных узлов и в нем только узел завершения"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, finish_node.nodeId).body)
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and finish_node.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки."

    @allure.story("После удаление примитивной переменной, указанной в Expression editor, узел расчета переменных "
                  "становится невалидным и возвращается в invalidNodeIds и сообщении об ошибке")
    @allure.title("Удалить переменную, указанную в EE, проверить, что ревалидация вернула 422, и узел расчета "
                  "переменных невалиден")
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_var", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_var")
         ])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.expression_var("primitive")
    @pytest.mark.smoke
    def test_calc_expression_primitive_revalidate(self, super_user, diagram_constructor,
                                                  diagram_calc_prim_v):
        calc_node: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
        with allure.step("Удаление входной переменной, указанной в Expression Editor"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            in_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
            del_param = list(filter(lambda param: param["parameterName"] != in_variable.parameterName,
                                    diagram_parameters.inOutParameters))
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], del_param)
            with allure.step("Проверка, что ревалидация вернула список невалидных узлов и в нем только узел расчета "
                             "переменных"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, calc_node.nodeId).body)
                calc_var_row = node_view.properties["calculate"][0]["rowKey"]
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and calc_node.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки." \
                       and node_view.validationPayload["nodeValidationMap"]["calculate"][calc_var_row]["expression"] == \
                       f'Переменные - {in_variable.parameterName} не найдены или не были рассчитаны'

    @allure.story("После удаление комплексной переменной, атрибут которой указан в Expression editor, узел расчета "
                  "переменных становится невалидным и возвращается в invalidNodeIds и сообщении об ошибке")
    @allure.title("Удалить переменную, атрибут которой указан в EE, проверить, что ревалидация вернула 422, "
                  "и узел расчета переменных невалиден")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_var", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                        varValue="out_var"),
         VariableParams(varName="input_var", varType="in", isArray=False, isComplex=True,
                        cmplxAttrInfo=[AttrInfo(attrName="int_attr1",
                                                intAttrType=IntValueType.int)])
         ])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.expression_var("complex")
    @pytest.mark.smoke
    def test_calc_expression_complex_revalidate(self, super_user, diagram_constructor,
                                                diagram_calc_prim_v):
        calc_node: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        with allure.step("Удаление комплексной переменной, атрибут которой указан в Expression Editor"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            in_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
            del_param = list(filter(lambda param: param["parameterName"] != in_variable.parameterName,
                                    diagram_parameters.inOutParameters))
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], del_param)
            with allure.step("Проверка, что ревалидация вернула список невалидных узлов и в нем только узел расчета "
                             "переменных"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, calc_node.nodeId).body)
                calc_var_row = node_view.properties["calculate"][0]["rowKey"]
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and calc_node.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки." \
                       and node_view.validationPayload["nodeValidationMap"]["calculate"][calc_var_row]["expression"] == \
                       f'Переменные - {in_variable.parameterName} не найдены или не были рассчитаны'

    @allure.story("Узел расчета переменных остаётся валидным при обращении через точку к методу массива в Expression "
                  "Editor")
    @allure.title("В Expression Editor обратиться к методу массива, проверить, что узел расчета переменных валиден")
    @pytest.mark.variable_data(
        [
            VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value, isConst=False,
                           varValue="in_out_var"),
            VariableParams(varName="input_var", varType="in", isArray=True, isComplex=True,
                           cmplxAttrInfo=[AttrInfo(attrName="int_attr1",
                                                   intAttrType=IntValueType.int)])
        ])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_calc_expression_array_method_revalidate(self, super_user, diagram_constructor):
        node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        with allure.step("Создание и расчет переменной путем обращения к методу массива в узле расчета"):
            input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, input_var.typeId).body
            )
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=True,
                is_compl=True,
                name="local_var",
                type_id=input_var.typeId,
                calc_val=f"${input_var.parameterName}.findAll{{element -> element.{complex_type.attributes[0]['attributeName']} > 2}}",
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                diagram_constructor["temp_version_id"],
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc.nodeId, body=node_calc_upd)
        with allure.step("Проверка, что узел расчета переменных валидный"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_calc.nodeId).body)
            assert node_view.validFlag

    @allure.story("После удаление примитивной переменной, указанной в Expression editor, узел ветвление "
                  "становится невалидным и возвращается в invalidNodeIds и сообщении об ошибке")
    @allure.title("Удалить переменную, указанную в EE, проверить, что ревалидация вернула 422, и узел ветвление "
                  "невалидный")
    @pytest.mark.variable_data([
        VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)
    ])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    @pytest.mark.branch_type("BRANCH_BY_CALCULATE_CONDITION")
    @pytest.mark.smoke
    def test_branch_expression_primitive_revalidate(self, super_user, diagram_constructor,
                                                    diagram_branch_saved):
        with allure.step("Удаление входной переменной, указанной в Expression Editor"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            in_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
            branch_node: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            del_param = list(filter(lambda param: param["parameterName"] != in_variable.parameterName,
                                    diagram_parameters.inOutParameters))
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], del_param)
            with allure.step("Проверка, что ревалидация вернула список невалидных узлов и в нем только узел ветвления"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, branch_node.nodeId).body)
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and branch_node.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки." \
                       and node_view.validationPayload["nodeValidationMap"]["condition"] == \
                       f'Переменные - {in_variable.parameterName} не найдены или не были рассчитаны'

    @allure.story("После удаление переменной пользовательского типа, атрибут которой указан в Expression editor, "
                  "узел ветвление становится невалидным и возвращается в invalidNodeIds и сообщении об ошибке")
    @allure.title("Удалить переменную, атрибут которой указан в EE, проверить, что ревалидация вернула 422, "
                  "и узел ветвление невалидный")
    @pytest.mark.variable_data([
        VariableParams(varName="in_out_var", varType="in_out", isArray=False, isComplex=True,
                       cmplxAttrInfo=[AttrInfo(attrName="int_attr1",
                                               intAttrType=IntValueType.int)])
    ])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    @pytest.mark.branch_type("BRANCH_BY_CALCULATE_CONDITION")
    @pytest.mark.smoke
    def test_branch_expression_complex_revalidate(self, super_user, diagram_constructor,
                                                  diagram_branch_saved):
        with allure.step("Получение информации об узле ветвление"):
            branch_node: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            in_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, in_variable.typeId).body
            )
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, branch_node.nodeId).body)
            branch_for_node: BranchNodeBranch = BranchNodeBranch.construct(
                **node_view.properties["branches"][0])
            default_path: DefaultBranch = DefaultBranch.construct(**node_view.properties["defaultPath"])
        with allure.step("Обновление узла ветвление"):
            node_br_properties = branch_node_properties(branching_type=node_view.properties["branchingType"],
                                                        condition=f"${in_variable.parameterName}."
                                                                  f"{complex_type.attributes[0]['attributeName']} + 1",
                                                        branching_value_type="1",
                                                        branches=[branch_for_node],
                                                        default_path=default_path)
            update_body = branch_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=diagram_constructor["temp_version_id"],
                                                properties=node_br_properties,
                                                operation="update")
            update_node(super_user, node_id=branch_node.nodeId, body=update_body)
        with allure.step("Удаление входной переменной, указанной в Expression Editor"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            in_out_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
            branch_node: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            del_param = list(filter(lambda param: param["parameterName"] != in_out_variable.parameterName,
                                    diagram_parameters.inOutParameters))
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], del_param)
            with allure.step("Проверка, что ревалидация вернула список невалидных узлов и в нем только узел ветвления"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, branch_node.nodeId).body)
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and branch_node.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки." \
                       and node_view.validationPayload["nodeValidationMap"]["condition"] == \
                       f'Переменные - {in_out_variable.parameterName} не найдены или не были рассчитаны'

    @allure.story("Узел ветвления остаётся валидным при обращении через точку к методу массива в Expression "
                  "Editor")
    @allure.title("В Expression Editor обратиться к методу массива, проверить, что узел ветвления валиден")
    @pytest.mark.variable_data([
        VariableParams(varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value),
        VariableParams(varName="in_var", varType="in", isArray=True, isComplex=True,
                       cmplxAttrInfo=[AttrInfo(attrName="int_attr1",
                                               intAttrType=IntValueType.int)])
    ])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    @pytest.mark.branch_type("BRANCH_BY_CALCULATE_CONDITION")
    @pytest.mark.smoke
    def test_branch_expression_array_method_revalidate(self, super_user, diagram_constructor, diagram_branch_saved):
        with allure.step("Получение информации об узле ветвление"):
            branch_node: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            in_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_var"]
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, in_variable.typeId).body
            )
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, branch_node.nodeId).body)
            branch_for_node: BranchNodeBranch = BranchNodeBranch.construct(
                **node_view.properties["branches"][0])
            default_path: DefaultBranch = DefaultBranch.construct(**node_view.properties["defaultPath"])
        with allure.step("Обновление узла ветвление"):
            node_br_properties = branch_node_properties(branching_type=node_view.properties["branchingType"],
                                                        condition=f"(${in_variable.parameterName}."
                                                                  f"findAll{{element -> element."
                                                                  f"{complex_type.attributes[0]['attributeName']} > 2}}[0])"
                                                                  f".{complex_type.attributes[0]['attributeName']}",
                                                        branching_value_type="1",
                                                        branches=[branch_for_node],
                                                        default_path=default_path)
            update_body = branch_node_construct(x=700, y=202.22915649414062,
                                                temp_version_id=diagram_constructor["temp_version_id"],
                                                properties=node_br_properties,
                                                operation="update")
            update_node(super_user, node_id=branch_node.nodeId, body=update_body)
        with allure.step("Проверка, что узел ветвления валидный"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, branch_node.nodeId).body)
            assert node_view.validFlag

    @allure.story("После удаление примитивной переменной, указанной в Expression editor, узел набор правил "
                  "становится невалидным и возвращается в invalidNodeIds и сообщении об ошибке")
    @allure.title("Удалить переменную, указанную в EE, проверить, что ревалидация вернула 422, и узел набор "
                  "правил")
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="out_rule_result", varType="out", varDataType=IntValueType.complex_type_rule.value,
                        isComplex=True, isArray=True, isConst=False)])
    @pytest.mark.nodes(["набор правил"])
    @pytest.mark.expression_var("primitive")
    @pytest.mark.smoke
    def test_rule_expression_primitive_revalidate(self, super_user, diagram_constructor,
                                                  diagram_ruleset_saved):
        rule_node: NodeViewShortInfo = diagram_constructor["nodes"]["набор правил"]
        with allure.step("Удаление входной переменной, указанной в Expression Editor"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            in_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
            del_param = list(filter(lambda param: param["parameterName"] != in_variable.parameterName,
                                    diagram_parameters.inOutParameters))
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], del_param,
                                      inner_vars=diagram_parameters.innerVariables)
            with allure.step("Проверка, что ревалидация вернула список невалидных узлов и в нем только узел набора "
                             "правил"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, rule_node.nodeId).body)
                rule_row = node_view.properties["rules"][0]["rowKey"]
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and rule_node.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки." \
                       and node_view.validationPayload["nodeValidationMap"]["rules"][rule_row]["ruleExpression"] == \
                       f'Переменные - {in_variable.parameterName} не найдены или не были рассчитаны'

    @allure.story("После удаление пользовательской переменной, атрибут которой указан в Expression editor, узел набор "
                  "правил становится невалидным и возвращается в invalidNodeIds и сообщении об ошибке")
    @allure.title("Удалить переменную, атрибут которой указан в EE, проверить, что ревалидация вернула 422, "
                  "и узел набор правил")
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", isArray=False, isComplex=True,
                        cmplxAttrInfo=[AttrInfo(attrName="int_attr1",
                                                intAttrType=IntValueType.int)]),
         VariableParams(varName="out_rule_result", varType="out", varDataType=IntValueType.complex_type_rule.value,
                        isComplex=True, isArray=True, isConst=False)])
    @pytest.mark.nodes(["набор правил"])
    @pytest.mark.expression_var("complex")
    @pytest.mark.smoke
    def test_rule_expression_complex_revalidate(self, super_user, diagram_constructor,
                                                diagram_ruleset_saved):
        rule_node: NodeViewShortInfo = diagram_constructor["nodes"]["набор правил"]
        with allure.step("Удаление входной переменной, указанной в Expression Editor"):
            diagram_parameters: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            in_variable: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
            del_param = list(filter(lambda param: param["parameterName"] != in_variable.parameterName,
                                    diagram_parameters.inOutParameters))
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], del_param,
                                      inner_vars=diagram_parameters.innerVariables)
            with allure.step("Проверка, что ревалидация вернула список невалидных узлов и в нем только узел набора "
                             "правил"):
                with pytest.raises(HTTPError) as e:
                    DiagramValidateResponseDto.construct(
                        **revalidate_node(super_user, diagram_constructor["temp_version_id"]).body)
                response = e.value.response.json()
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, rule_node.nodeId).body)
                rule_row = node_view.properties["rules"][0]["rowKey"]
                assert response["httpCode"] == 422 \
                       and len(response["invalidNodeIds"]) == 1 \
                       and rule_node.nodeId in response["invalidNodeIds"] \
                       and not node_view.validFlag \
                       and response["message"] == f"На узле - {node_view.nodeName}, есть ошибки." \
                       and node_view.validationPayload["nodeValidationMap"]["rules"][rule_row]["ruleExpression"] == \
                       f'Переменные - {in_variable.parameterName} не найдены или не были рассчитаны'

    @allure.story("Узел набор правил остаётся валидным при обращении через точку к методу массива в Expression "
                  "Editor")
    @allure.title("В Expression Editor обратиться к методу массива, проверить, что узел набора правил валиден")
    @pytest.mark.variable_data(
        [
            VariableParams(varName="out_rule_result", varType="out", varDataType=IntValueType.complex_type_rule.value,
                           isComplex=True, isArray=True, isConst=False),
            VariableParams(varName="input_var", varType="in", isArray=True, isComplex=True,
                           cmplxAttrInfo=[AttrInfo(attrName="int_attr1",
                                                   intAttrType=IntValueType.int)])
        ])
    @pytest.mark.nodes(["набор правил"])
    @pytest.mark.smoke
    def test_rule_expression_array_method_revalidate(self, super_user, diagram_constructor, diagram_ruleset_saved):
        rule_node: NodeViewShortInfo = diagram_ruleset_saved["diagram_nodes"]["набор правил"]
        input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["input_var"]
        complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
            **get_custom_type(super_user, input_var.typeId).body
        )
        with allure.step("Обновление правила в узле набор правил"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, rule_node.nodeId).body)
            node_view.properties["rules"][0]["ruleExpression"] = f"(${input_var.parameterName}." \
                                                                 f"findAll{{element -> element.{complex_type.attributes[0]['attributeName']}" \
                                                                 f" > 2}}[0]).{complex_type.attributes[0]['attributeName']} > 1"
        with allure.step("Обновление узла набора правил"):
            rule_v: RulesetVariableProperties = RulesetVariableProperties.construct(
                **node_view.properties["ruleVariable"])
            node_rule_upd = ruleset_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=diagram_constructor["temp_version_id"],
                rule_variable=rule_v,
                rules=node_view.properties["rules"],
                operation="update",
            )
            update_node(
                super_user, node_id=rule_node.nodeId, body=node_rule_upd
            )
        with allure.step("Проверка, что узел набор правил валидный"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, rule_node.nodeId).body)
            assert node_view.validFlag
