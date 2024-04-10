import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    ResponseDto,
    DiagramViewDto,
    NodeViewShortInfo,
    DiagramInOutParameterFullViewDto,
    NodeViewWithVariablesDto,
    NodeValidateDto,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version,
)
from products.Decision.framework.steps.decision_steps_nodes import (
    create_node,
    get_node_by_id,
    delete_node_by_id,
    update_node,
    create_link,
    validate_node,
)
from products.Decision.utilities.custom_models import IntValueType, VariableParams, NodeFullInfo, IntNodeType
from products.Decision.utilities.node_cunstructors import (
    branch_node_construct,
    branch,
    default_branch,
    branch_node_properties,
    link_construct,
)


@allure.epic("Диаграммы")
@allure.feature("Узел ветвление")
class TestBranchNode:
    @allure.story("Узел можно создать с NodeType = 10")
    @allure.title(
        "Создать диаграмму с узлом ветвления без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15454")
    @pytest.mark.smoke
    def test_create_node_branch_empty(self, super_user, create_temp_diagram):
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла ветвления"):
            node_sub = branch_node_construct(
                700, 202.22915649414062, template["versionId"], None
            )
            node_sub_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_sub).body
            )
            node_sub_id = node_sub_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step("Проверка, что создался нужный узел"):
            assert diagram.nodes[str(node_sub_id)].nodeTypeId == 10

    @allure.story("Узел ветвления можно удалить")
    @allure.title("Удалить узел ветвления без параметров")
    @pytest.mark.scenario("DEV-15454")
    @pytest.mark.smoke
    def test_delete_node_branch(self, super_user, create_temp_diagram):
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла ветвления"):
            node_branch = branch_node_construct(
                700, 202.22915649414062, template["versionId"], None
            )
            node_branch_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_branch).body
            )
            node_branch_id = node_branch_response.uuid
        with allure.step("Удаление узла ветвления по id"):
            delete_node_by_id(super_user, node_branch_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_branch_id).status == 404

    @allure.story("У корректного узла ветвления valid flag false")
    @allure.title("Создать диаграмму с узлом ветвления")
    @pytest.mark.scenario("DEV-15454")
    @pytest.mark.smoke
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_update_branch_node_correct(self, super_user, diagram_constructor):
        temp_version_id = diagram_constructor["diagram_info"].versionId
        link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
        link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
        node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
        node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
        node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
        diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Обновление узла ветвления"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="GREATER",
                value_from="5",
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f2_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type="1",
                branches=[branch_for_node],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
            update_node(
                super_user,
                node_id=node_branch.nodeId,
                body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId, properties=node_br_properties
                ),
            )
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_branch.nodeId).body
            )
        assert (
                node_view.validFlag
                and node_view.properties["branches"][0]["nodeId"] == node_end1.nodeId
                and node_view.properties["branches"][0]["linkId"] == link_b_f1_id
                and node_view.properties["defaultPath"]["nodeId"] == node_end2.nodeId
                and node_view.properties["defaultPath"]["linkId"] == link_b_f2_id
        )

    @allure.story(
        "Значения элемента в условиях по интервалу ветвления не должны пересекаться"
    )
    @allure.title(
        "В условии задаем интервал с пересекающимися значениями, ожидаем ошибку"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_node_intersection(self, super_user, diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Создание связи для второй ветви узла Ветвления"):
            link_b_f21 = link_construct(temp_version_id, node_branch.nodeId, node_end2.nodeId)
            link_b_f21_create_response: ResponseDto = ResponseDto.construct(
                **create_link(super_user, body=link_b_f21).body
            )
            link_b_f21_id = link_b_f21_create_response.uuid
        with allure.step("В узле Ветвления при обновление задаем пересекающиеся значения при заданном "
                         "операторе INTERVAL' с условием ветвления - 'По значению элемента'"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="INTERVAL",
                value_from=5,
                value_from_include_flag=False,
                value_to=8,
                value_to_include_flag=True,
            )
            branch_for_node_2 = branch(
                link_id=link_b_f2_id,
                node_id=node_end2.nodeId,
                operator="INTERVAL",
                value_from=8,
                value_from_include_flag=True,
                value_to=10,
                value_to_include_flag=False,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f21_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type=IntValueType.int,
                branches=[branch_for_node, branch_for_node_2],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)
            validation_message = "Значения элемента в условиях ветвления не должны пересекаться"
        with allure.step(
                "Проверка на соответствие текста ошибки"
        ):
            assert validation_resp.validationPayload["nodeValidationMap"]["branches"][branch_for_node.rowKey][
                       "value"] == validation_message
            assert validation_resp.validationPayload["nodeValidationMap"]["branches"][branch_for_node_2.rowKey][
                       "value"] == validation_message

    @allure.story("оператор соответствует типу данных элемента")
    @allure.title(
        "В условии ветвления указываем оператор не соответствующий типу данных указанных в блоке ветвления "
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("type_id, branching_val",
                             [pytest.param(IntValueType.str, "'string'", marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.str.value)])]),
                              pytest.param(IntValueType.bool, True, marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.bool.value)])])])
    @pytest.mark.parametrize(
        "operator, operator_value",
        [
            ("GREATER", ">"),
            ("LESS", "<"),
            ("GREATER_OR_EQUAL", ">="),
            ("LESS_OR_EQUAL", "<="),
        ],
    )
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_condition_type_operator(
            self, super_user, type_id, branching_val, operator, operator_value, diagram_constructor
    ):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Обновление узла ветвления. Указываем оператор не применимый"
                         " к типу переменной (строковый, логический)"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator=operator,
                value_from=branching_val,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f2_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type=type_id,
                branches=[branch_for_node],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)
            validation_message = f"Указанный в условии ветвления оператор - {operator_value} " \
                                 f"не применим к указанному типу значения"
        with allure.step(
                 "Проверка на cоответствия текста ошибки"
         ):
            assert validation_resp.validationPayload["nodeValidationMap"]["branches"][branch_for_node.rowKey][
                       "operator"] == validation_message

    @allure.story("оператор соответствует типу данных элемента")
    @allure.title(
        "В условии ветвления указываем оператор interval не соответствующий типу данных указанных"
        " в блоке ветвления"
    )
    @pytest.mark.parametrize("type_id, branching_val_1, branching_val_2",
                             [pytest.param(IntValueType.str, "'string'", "'string2'", marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.str.value)])]),
                              pytest.param(IntValueType.bool, True, False, marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.bool.value)])])])
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_condition_type_operator_interval(
            self, super_user, type_id, branching_val_1, branching_val_2, diagram_constructor
    ):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Создание связи для второй ветви узла Ветвления"):
            link_b_f21 = link_construct(temp_version_id, node_branch.nodeId, node_end2.nodeId)
            link_b_f21_create_response: ResponseDto = ResponseDto.construct(
                **create_link(super_user, body=link_b_f21).body
            )
            link_b_f21_id = link_b_f21_create_response.uuid
        with allure.step("Обновление узла Ветвления. Указываем оператор INTERVAL не применимый"
                         " к типу переменной (строковый, логический)"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="INTERVAL",
                value_from=branching_val_1,
                value_from_include_flag=False,
                value_to=branching_val_1,
                value_to_include_flag=False,
            )
            branch_for_node_2 = branch(
                link_id=link_b_f2_id,
                node_id=node_end2.nodeId,
                operator="INTERVAL",
                value_from=branching_val_2,
                value_from_include_flag=False,
                value_to=branching_val_2,
                value_to_include_flag=False,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f21_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type=type_id,
                branches=[branch_for_node, branch_for_node_2],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)
            validation_message = f"Указанный в условии ветвления оператор - ()" \
                                 f" не применим к указанному типу значения"
        with allure.step(
                "Проверка на cоответствие текста ошибки"
        ):
            assert validation_resp.validationPayload["nodeValidationMap"]["branches"][branch_for_node.rowKey][
                       "operator"] == validation_message
            assert validation_resp.validationPayload["nodeValidationMap"]["branches"][branch_for_node_2.rowKey][
                       "operator"] == validation_message

    @allure.story("оператор соответствует типу данных элемента")
    @allure.title("Указываем оператор в условии ветвления соответствующий типу данных")
    @pytest.mark.parametrize("type_id, branching_val",
                             [pytest.param(IntValueType.str, "'string'", marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.str.value)])]),
                              pytest.param(IntValueType.bool, True, marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.bool.value)])])])
    @pytest.mark.smoke
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_condition_type_operator_valid(self, super_user, type_id, branching_val,  diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Обновление узла ветвления. Указываем оператор EQUAL применимый"
                         " к типу переменной (строковый, логический)"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="EQUAL",
                value_from=branching_val,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f2_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type=type_id,
                branches=[branch_for_node],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)

        with allure.step(
                "Проверка успешной валидации"
        ):
            assert validation_resp.operation == "validate"

    @allure.story("Предусмотрена валидация на то, что оператор соответствует типу данных элемента: если тип элемента "
                  "condition равен 0 (Дробный), 1 (Целочисленный), 3 (Дата), 5 (Дата_время), 6 (Время), "
                  "7 (Целочисленный (LONG)) то может применяться любая операция (поле operator принимает любое"
                  " допустимое значение).")
    @allure.title("Проверяем что с типом данных 0, 1, 7 может применяться любой оператор")
    @pytest.mark.parametrize("operator", ["EQUAL", "GREATER", "LESS", "GREATER_OR_EQUAL", "LESS_OR_EQUAL"])
    @pytest.mark.parametrize("type_id, branching_val",
                             [pytest.param(IntValueType.float, "5.6", marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.float.value)])]),
                              pytest.param(IntValueType.int, 5, marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])]),
                              pytest.param(IntValueType.long, 507, marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.long.value)])])
                              ])
    @pytest.mark.smoke
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_node_all_operators_available_for_nums(self, super_user, type_id, operator,
                                                          branching_val, diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Обновление узла ветвления. Указываем оператор применимый"
                         " к типу переменной (целочисленный, дробный, целочисленный(LONG))"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator=operator,
                value_from=branching_val,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f2_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type=type_id,
                branches=[branch_for_node],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)

        with allure.step(
                "Проверка успешной валидации"
        ):
            assert validation_resp.operation == "validate"

    @allure.story("Предусмотрена валидация на то, что оператор соответствует типу данных элемента: если тип элемента "
                  "condition равен 0 (Дробный), 1 (Целочисленный), 3 (Дата), 5 (Дата_время), 6 (Время), "
                  "7 (Целочисленный (LONG)) то может применяться любая операция (поле operator принимает любое"
                  " допустимое значение).")
    @allure.title("Проверяем что с типом данных 0, 1, 7 может применяться любой оператор(interval)")
    @pytest.mark.smoke
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("type_id, branching_val_1, branching_val_2, branching_val_3",
                             [pytest.param(IntValueType.float, 5.6, 5.9, 6.2,  marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.float.value)])]),
                              pytest.param(IntValueType.int, 5, 7, 9, marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])]),
                              pytest.param(IntValueType.long, 507, 600, 800, marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.long.value)])])
                              ])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_node_all_operators_available_for_nums_interval(self, super_user, type_id, branching_val_1,
                                                                   branching_val_2, branching_val_3, diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Создание связи для второй ветви узла Ветвления"):
            link_b_f21 = link_construct(temp_version_id, node_branch.nodeId, node_end2.nodeId)
            link_b_f21_create_response: ResponseDto = ResponseDto.construct(
                **create_link(super_user, body=link_b_f21).body
            )
            link_b_f21_id = link_b_f21_create_response.uuid
        with allure.step("Валидация узла Ветвления, Указываем оператор INTERVAL пременимый к переменным "
                         "с типом(целочисленный, дробный, целочисленный(LONG))"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="INTERVAL",
                value_from=branching_val_1,
                value_from_include_flag=False,
                value_to=branching_val_2,
                value_to_include_flag=False,
            )
            branch_for_node_2 = branch(
                link_id=link_b_f2_id,
                node_id=node_end2.nodeId,
                operator="INTERVAL",
                value_from=branching_val_2,
                value_from_include_flag=False,
                value_to=branching_val_3,
                value_to_include_flag=False,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f21_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type=type_id,
                branches=[branch_for_node, branch_for_node_2],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)

        with allure.step(
                "Проверка успешной валидации"
        ):
            assert validation_resp.operation == "validate"


    @allure.story(
        "Предусмотрена валидация на то, что оператор соответствует типу данных элемента: если тип элемента "
        "condition равен 0 (Дробный), 1 (Целочисленный), 3 (Дата), 5 (Дата_время), 6 (Время), "
        "7 (Целочисленный (LONG)) то может применяться любая операция (поле operator принимает любое"
        " допустимое значение)."
    )
    @allure.title(
        "Проверяем что с типом данных 3, 5, 6 может применяться любой оператор"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("type_id, branching_val",
                             [pytest.param(IntValueType.date, "2023-03-24", marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.date.value)])]),
                              pytest.param(IntValueType.dateTime, "2023-03-24 17:23:09.000", marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.dateTime.value)])]),
                              pytest.param(IntValueType.time, "00:02:00", marks=[
                                  pytest.mark.variable_data([VariableParams(
                                      varName="in_out_var", varType="in_out", varDataType=IntValueType.time.value)])])
                              ])
    @pytest.mark.parametrize(
        "operator", ["EQUAL", "GREATER", "LESS", "GREATER_OR_EQUAL", "LESS_OR_EQUAL"]
    )
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    @allure.issue(url="DEV-10182")
    @allure.issue(url="DEV-10180")
    @pytest.mark.smoke
    def test_branch_node_all_operators_available_for_nums_2(self, type_id, operator, branching_val,
                                                            super_user, diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_out_var"]
        with allure.step("Обновление узла ветвления. Указываем оператор пременимый к переменным "
                         "с типом(Дата, Дата_время, Время)"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator=operator,
                value_from=branching_val,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f2_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_ELEMENT",
                condition=diagram_param.parameterName,
                branching_value_type=type_id,
                branches=[branch_for_node],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Проверка что может применяться любая операция."):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)
        with allure.step(
                "На валидации код 200 - успешно(в случае ошибки валидации код 400)"
        ):
            assert validation_resp.httpCode == 200 and validation_resp.operation == "validate"

    @allure.story(
        "Предусмотрена валидация на то, что если branchingType = 'BRANCH_BY_PERCENT', то значение - "
        'положительное число.Текст ошибки: "При ветвлении по процентам значение должно быть'
        ' положительным числом, сейчас данное значение %s"'
    )
    @allure.title("ВВодим в условие ветвления по процентам отрицательное число")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("type_id, branching_val",
                             [pytest.param(IntValueType.int, -5, marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])])])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_node_percent(self, super_user, type_id, branching_val, diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
        with allure.step("Обновление узла ветвления. Задаем условие ветвления - по прценту "
                         "и в поле значение вводим отрицательное число"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="EQUAL",
                value_from=branching_val,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f2_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_PERCENT",
                condition=None,
                branching_value_type=type_id,
                branches=[branch_for_node],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)
            validation_message = f"При ветвлении по процентам значение должно быть " \
                                 f"положительным числом, сейчас данное значение {branching_val}"
            with allure.step(
                    "Проверка на cоответствие текста ошибки"
            ):
                assert validation_resp.validationPayload["nodeValidationMap"]["branches"][branch_for_node.rowKey][
                       "value"] == validation_message

    @allure.story(
        "Предусмотрена валидация на то, что если branchingType = 'BRANCH_BY_PERCENT', то сумма процентов по "
        "каждой ветке не превышает 100%.Текст ошибки: 'Сумма процентов должна быть меньше 100'"
    )
    @allure.title(
        "В блоке ветвления по процентам задаем значения сумма которых больше 100%"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("type_id, branching_val_1, branching_val_2",
                             [pytest.param(IntValueType.int, 50, 75, marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])])])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_node_percent_sum(self, super_user, type_id, branching_val_1, branching_val_2, diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
        with allure.step("Создание связи для второй ветви узла Ветвления"):
            link_b_f21 = link_construct(temp_version_id, node_branch.nodeId, node_end2.nodeId)
            link_b_f21_create_response: ResponseDto = ResponseDto.construct(
                **create_link(super_user, body=link_b_f21).body
            )
            link_b_f21_id = link_b_f21_create_response.uuid
        with allure.step("Обновление узла Ветвления. Задаем условие ветвления - по прценту "
                         "и в поле значение вводим проценты, в сумме, которые дают больше 100%"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="EQUAL",
                value_from=branching_val_1,
                value_from_include_flag=False,
                value_to=None,
                value_to_include_flag=False,
            )
            branch_for_node_2 = branch(
                link_id=link_b_f2_id,
                node_id=node_end2.nodeId,
                operator="EQUAL",
                value_from=branching_val_2,
                value_from_include_flag=False,
                value_to=None,
                value_to_include_flag=False,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f21_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_PERCENT",
                condition=None,
                branching_value_type=type_id,
                branches=[branch_for_node, branch_for_node_2],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)
        validation_message = ["Сумма процентов должна быть меньше 100", "На узле есть ошибки"]
        with allure.step(
                "Проверка на cоответствие текста ошибки"
        ):
            assert validation_resp.validationPayload["commonNodeValidationMessages"] == validation_message

    @allure.story("Нет ошибки валидации при одинаковых значениях процентов")
    @allure.title("В блоке ветвления по процентам вводим два одинаковых значения в сумме дающих 100 %")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.smoke
    @pytest.mark.parametrize("type_id, branching_val",
                             [pytest.param(IntValueType.int, 50, marks=[
                                 pytest.mark.variable_data([VariableParams(
                                     varName="in_out_var", varType="in_out", varDataType=IntValueType.int.value)])])])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_branch_node_percent_the_same(self, super_user, type_id, branching_val, diagram_constructor):
        with allure.step("Создание временной версии диаграммы"):
            temp_version_id = diagram_constructor["diagram_info"].versionId
            link_b_f1_id = diagram_constructor["links"]["Ветвление->Завершение"]
            link_b_f2_id = diagram_constructor["links"]["Ветвление->Завершение_1"]
            node_end1: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            node_end2: NodeViewShortInfo = diagram_constructor["nodes"]["завершение_1"]
            node_branch: NodeViewShortInfo = diagram_constructor["nodes"]["Ветвление"]
        with allure.step("Создание связи для второй ветви узла Ветвления"):
            link_b_f21 = link_construct(temp_version_id, node_branch.nodeId, node_end2.nodeId)
            link_b_f21_create_response: ResponseDto = ResponseDto.construct(
                **create_link(super_user, body=link_b_f21).body
            )
            link_b_f21_id = link_b_f21_create_response.uuid
        with allure.step("Валидация узла Ветвления. Задаем условие ветвления - по прценту "
                         "и в поле значение вводим проценты, в сумме, которые дают 100%"):
            branch_for_node = branch(
                link_id=link_b_f1_id,
                node_id=node_end1.nodeId,
                operator="EQUAL",
                value_from=branching_val,
                value_from_include_flag=False,
                value_to=None,
                value_to_include_flag=False,
            )
            branch_for_node_2 = branch(
                link_id=link_b_f2_id,
                node_id=node_end2.nodeId,
                operator="EQUAL",
                value_from=branching_val,
                value_from_include_flag=False,
                value_to=None,
                value_to_include_flag=False,
            )
            default_path = default_branch(node_id=node_end2.nodeId, link_id=link_b_f21_id)
            node_br_properties = branch_node_properties(
                branching_type="BRANCH_BY_PERCENT",
                condition=None,
                branching_value_type=type_id,
                branches=[branch_for_node, branch_for_node_2],
                default_path=default_path,
            )
            update_body = branch_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=node_br_properties,
                operation="update",
            )
        with allure.step("Валидация узла Ветвления"):
            validation_resp: ResponseDto = ResponseDto(**validate_node(super_user, node_id=node_branch.nodeId,
                                                                       body=NodeValidateDto.construct(
                                                                           nodeTypeId=update_body.nodeTypeId,
                                                                           properties=node_br_properties
                                                                       )).body)

        with allure.step(
                "Проверка успешной валидации"
        ):
            assert validation_resp.httpCode == 200 and validation_resp.operation == "validate"

