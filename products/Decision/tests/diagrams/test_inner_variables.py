import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import NodeViewShortInfo, NodeValidateDto, NodeViewWithVariablesDto, \
    DiagramParameterDto, DiagramInnerVariableFullViewDto, DiagramValidateResponseDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_parameters, update_diagram_parameters, \
    validate_diagram
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id, delete_node_by_id
from products.Decision.utilities.custom_models import VariableParams, IntValueType
from products.Decision.utilities.node_cunstructors import variables_for_node, node_update_construct, node_construct


@allure.epic("Диаграммы")
@allure.feature("Внутренние переменные")
@pytest.mark.scenario("DEV-11350")
class TestDiagramsInnerVariables:
    @allure.story("Созданная на узле переменная появляется в списке внутренних параметров диаграммы")
    @allure.title("Создать на узле расчет переменных переменную с типом int, проверить, что появилась во внутренних "
                  "параметрах")
    @pytest.mark.scenario("DEV-11350")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_local_variable_create(self, super_user, diagram_constructor):
        flg = 0
        with allure.step("Получение информации об узле"):
            node_calc_var: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        with allure.step("Создание на узле внутренней переменной"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=False,
                is_compl=False,
                name="local_var",
                type_id=IntValueType.int.value,
                calc_val="5",
                calc_type_id=IntValueType.int.value
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                diagram_constructor["temp_version_id"],
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc_var.nodeId, body=node_calc_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_calc_upd.nodeTypeId,
                            properties=node_calc_upd.properties))
        with allure.step("Получение центрального узла диаграммы"):
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_calc_var.nodeId).body
            )
        with allure.step("Получение переменных диаграммы"):
            inner_param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
        with allure.step("Проверка, что переменная, созданная на узле, появилась во внутренних параметрах диаграммы, "
                         "и она одна"):
            for param in param_check_node_view.availableToCalc:
                if inner_param_check.innerVariables[0]["parameterName"] == param["variableName"]:
                    flg = 1
                    break
            assert flg == 1 and len(inner_param_check.innerVariables) == 1

    @allure.story("При удаление узла где создалась  внутренняя переменная "
                  "она не пропадает из списке внутренних параметров диаграммы")
    @allure.title("Создать на узле расчет переменных переменную с типом int,"
                  " удалить узел, проверить что не удалилась из списка внутренних переменных диаграммы")
    @pytest.mark.scenario("DEV-11350")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_local_variable_delete_node(self, super_user, diagram_constructor):
        with allure.step("Получение информации об узле"):
            node_calc_var: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        with allure.step("Создание на узле внутренней переменной"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=False,
                is_compl=False,
                name="local_var",
                type_id=IntValueType.int.value,
                calc_val="5",
                calc_type_id=IntValueType.int.value
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                diagram_constructor["temp_version_id"],
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc_var.nodeId, body=node_calc_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_calc_upd.nodeTypeId,
                            properties=node_calc_upd.properties))

        with allure.step("Удаление узла, на котором создалась переменная"):
            delete_node_by_id(super_user, node_calc_var.nodeId)

        with allure.step("Получение переменных диаграммы"):
            inner_param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)

        with allure.step("Проверка, что переменная, созданная на узле, с удалением узла,"
                         " пропала из внутренних параметрах диаграммы"):
            assert inner_param_check.innerVariables is not None

    @allure.story("При удаление внутреннуй переменной в списке внутренних параметров диаграммы"
                  "она пропадает из списке внутренних параметров диаграммы и в узле где создалась")
    @allure.title("Создать на узле расчет переменных переменную с типом int,"
                  " удалить переменную из списка внутренних переменных диаграммы, "
                  "проверить что удалилась из списка внутренних переменных диаграммы и на узле")
    @pytest.mark.scenario("DEV-11350")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_local_variable_delete(self, super_user, diagram_constructor):
        with allure.step("Получение информации об узле"):
            flg = 0
            node_calc_var: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        with allure.step("Создание на узле внутренней переменной"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=False,
                is_compl=False,
                name="local_var",
                type_id=IntValueType.int.value,
                calc_val="5",
                calc_type_id=IntValueType.int.value
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                diagram_constructor["temp_version_id"],
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc_var.nodeId, body=node_calc_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_calc_upd.nodeTypeId,
                            properties=node_calc_upd.properties))

        with allure.step("Удаление внутренней переменной в списке внутренних параметров диаграммы"):
            param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], param_check.inOutParameters,
                                      inner_vars=[])

        with allure.step("Получение переменных диаграммы"):
            inner_param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)

        with allure.step("Получение центрального узла диаграммы"):
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_calc_var.nodeId).body
            )

        with allure.step("Проверка, что переменная, созданная на узле, с удалением из списка внутренних переменных,"
                         " пропала из внутренних параметрах диаграммы и из узла где была создана"):
            for param in param_check_node_view.availableToCalc:
                if param_check.innerVariables[0]["parameterName"] == param["variableName"]:
                    flg = 1
                    break
            assert flg == 0 and inner_param_check.innerVariables is None

    @allure.story("При изменение типа или признака массива у внутренней переменной в списке внутренних параметров "
                  "диаграммы она изменяется в списке внутренних параметров диаграммы и в узле где создалась")
    @allure.title("Создать на узле расчет переменных переменную с типом int,"
                  " изменить переменную из списка внутренних переменных диаграммы, "
                  "проверить что изменилась  и на узле")
    @pytest.mark.scenario("DEV-11350")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.parametrize("type_ids", [0, 2, 3, 4, 5, 6, 7])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_local_variable_change(self, super_user, diagram_constructor, type_ids):
        with allure.step("Получение информации об узле"):
            node_calc_var: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        with allure.step("Создание на узле внутренней переменной"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=False,
                is_compl=False,
                name="local_var",
                type_id=IntValueType.int.value,
                calc_val="5",
                calc_type_id=IntValueType.int.value
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                diagram_constructor["temp_version_id"],
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc_var.nodeId, body=node_calc_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_calc_upd.nodeTypeId,
                            properties=node_calc_upd.properties))

        with allure.step("Изменение внутренней переменной в списке внутренних параметров диаграммы"):
            param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            inner_var = DiagramInnerVariableFullViewDto.construct(
                parameterName=param_check.innerVariables[0]["parameterName"],
                typeId=type_ids,
                dictFlag=param_check.innerVariables[0]["dictFlag"],
                arrayFlag=True,
                complexFlag=param_check.innerVariables[0]["complexFlag"],
                parameterVersionId=param_check.innerVariables[0]["parameterVersionId"],
                parameterId=param_check.innerVariables[0]["parameterId"]
            )
            param_check_2: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], param_check.inOutParameters,
                                      [inner_var])

        with allure.step("Получение переменных диаграммы"):
            inner_param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)

        with allure.step("Получение центрального узла диаграммы"):
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_calc_var.nodeId).body
            )

        with allure.step("Проверка, что переменная, созданная на узле, с изменением типа и признака массива изменилась "
                         " и в узле где была создана"):
            assert any(item["typeId"] == str(type_ids) and item["isArray"]
                       for item in param_check_node_view.availableToCalc) and \
                   len(inner_param_check.innerVariables) == 1

    @allure.story("После удаления внутренней переменной, при валидации диаграммы "
                  "в описании ошибке все узлы в которых используется внутренняя переменная")
    @allure.title("Создать внутреннюю переменную в узле Расчета переменных, в узле Завершения "
                  "намаппить  внутреннюю переменную на выходной атрибут, "
                  "удалить переменную, провалидировать диаграмму")
    @pytest.mark.scenario("DEV-11350")
    @pytest.mark.variable_data(
        [VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_local_variable_delete_missing_in_nodes(self, super_user, diagram_constructor):
        with allure.step("Получение информации об узле"):
            node_calc_var: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        with allure.step("Создание на узле внутренней переменной"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=False,
                is_compl=False,
                name="local_var",
                type_id=IntValueType.int.value,
                calc_val="5",
                calc_type_id=IntValueType.int.value
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                diagram_constructor["temp_version_id"],
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc_var.nodeId, body=node_calc_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_calc_upd.nodeTypeId,
                            properties=node_calc_upd.properties))
        with allure.step("Получение переменных диаграммы"):
            inner_param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)

        with allure.step("Маппинг внутренней переменной на выходной атрибут в узле Завершения"):
            node_finish_id = diagram_constructor["node_end_id"]
            var = diagram_constructor["variables"]["out_int"]
            finish_variable = variables_for_node(
                node_type="finish_out",
                is_arr=False,
                is_compl=False,
                name=var.parameterName,
                param_name=inner_param_check.innerVariables[0]["parameterName"],
                type_id=var.typeId,
                vers_id=var.parameterVersionId
            )

            node_finish_upd = node_update_construct(1800, 202, "finish",
                                                    temp_version_id=diagram_constructor["temp_version_id"],
                                                    variables=[finish_variable])
            update_node(super_user,
                        node_id=node_finish_id,
                        body=node_finish_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_finish_upd.nodeTypeId,
                            properties=node_finish_upd.properties))
        with allure.step("Удаление внутренней переменной в списке внутренних параметров диаграммы"):
            param_check: DiagramParameterDto = DiagramParameterDto.construct(
                **get_diagram_parameters(super_user, diagram_constructor["temp_version_id"]).body)
            update_diagram_parameters(super_user, diagram_constructor["temp_version_id"], param_check.inOutParameters,
                                      inner_vars=[])
        with allure.step("Валидация диаграммы"):
            with pytest.raises(HTTPError, match="422"):
                validate = DiagramValidateResponseDto.construct(
                    **validate_diagram(super_user, diagram_constructor["temp_version_id"]).body)
                assert (
                        validate["httpCode"] == 422
                        and any(node_id == node_finish_id for node_id in validate.invalidNodeIds)
                        and (node_id == node_calc_var.nodeId for node_id in validate.invalidNodeIds)
                )
