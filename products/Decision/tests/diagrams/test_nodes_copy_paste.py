import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import \
    ResponseDto, DiagramViewDto, NodeViewWithVariablesDto, ParameterType
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version, \
    update_diagram_parameters, get_diagram_parameters
from products.Decision.framework.steps.decision_steps_nodes import \
    copy_nodes, paste_nodes, get_node_by_id
from products.Decision.runtime_tests.runtime_fixtures.branch_fixtures import *
from products.Decision.runtime_tests.runtime_fixtures.var_calc_fixtures import *
from products.Decision.utilities.custom_models import IntNodeType, VariableParams, IntValueType
from products.Decision.utilities.custom_models import NodeFullInfo
from products.Decision.utilities.variable_constructors import variable_construct


@allure.epic("Диаграммы")
@allure.feature("Копирование узлов")
class TestDiagramsCopyNode:
    @allure.story("Возможно скопировать и вставить одиночный узел в рамках одной диаграммы")
    @allure.title("Скопировать и вставить узел завершения в одну и ту же диаграмму, проверить, что маппинги идентичны")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect",
                             [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    @allure.issue('DEV-18002')
    @pytest.mark.scenario("DEV-6873")
    def test_copypaste_single_end_node_same_diagram(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получаем информацию о диаграмме и узле"):
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            copying_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            nodes_before_pasting = get_diagram_by_version(super_user,
                                                          temp_version_id).body["nodes"]

        with allure.step("Копируем узел"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=temp_version_id,
                                                                          node_ids=[copying_node_id]).body)
            copy_id = copy_result.uuid

        with allure.step("Вставляем узел"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=temp_version_id).body["diagram"])
            nodes_after_pasting = paste_result.nodes
        with allure.step("Получаем свойства скопированного и вставленного узла"):
            copied_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                                                        copying_node_id).body)
            # так как возвращается целиком вся диаграмма - преобразуем узлы в множества и вычитаем старое из нового
            pasted_node_id = (set(nodes_after_pasting.keys()) - set(nodes_before_pasting.keys())).pop()
            pasted_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                                                        pasted_node_id).body)
        with allure.step("Проверяем, что свойства вставленного узла равны свойствам скопированного узла"):
            assert sorted(pasted_node.properties['mappingVariables'], key=lambda k: k['rowKey']) == \
                   sorted(copied_node.properties['mappingVariables'], key=lambda k: k['rowKey'])

    @allure.story("Возможно скопировать и вставить одиночный узел расчета переменных в рамках разных диаграмм")
    @allure.title("Скопировать и вставить узел в разные диаграммы, проверить, что маппинги сохранились")
    @pytest.mark.smoke
    @pytest.mark.scenario("DEV-6873")
    @pytest.mark.variable_data([VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
                                VariableParams(varName="out_var", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    def test_copypaste_single_calc_node_different_diagram(self, super_user,
                                                          diagram_calc_prim_v,
                                                          create_temp_diagram_gen):
        with allure.step("Получаем информацию о диаграммах и копируемом узле"):
            source_temp_version_id = diagram_calc_prim_v["diagram_data"].versionId
            target_diagram_version_id = create_temp_diagram_gen.create_template().versionId
            copying_node_id = diagram_calc_prim_v["calc_node_id"]
        with allure.step("Копируем узел и получаем идентификатор копии"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=[copying_node_id]).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узел в другую диаграмму"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
            nodes_after_pasting = paste_result.nodes
        with allure.step("Получаем свойства скопированного и вставленного узла"):
            copied_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                                                        copying_node_id).body)
            pasted_node_id = list(nodes_after_pasting.keys())[0]
            pasted_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                                                        pasted_node_id).body)
        with allure.step(
                "Проверяем, что свойства вставленного узла в другую диаграмму равны свойствам скопированного узла"):
            assert sorted(pasted_node.properties['calculate'], key=lambda k: k['rowKey']) == \
                   sorted(copied_node.properties['calculate'], key=lambda k: k['rowKey'])

    @allure.story("При вставке узла завершения в новую диаграмму мапиинги сохраняются, а идентификаторы "
                  "переменных не меняются ")
    @allure.title("Скопировать и вставить узел завершенияв разные диаграммы, проверить, что маппинги переменных "
                  "остались а идентификаторы выходных переменных не изменились")
    @pytest.mark.smoke
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect",
                             [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.scenario("DEV-6873")
    def test_copypaste_end_node_different_diagram(self, super_user,
                                                  diagram_all_prim_v_one_node_indirect,
                                                  create_temp_diagram_gen):
        with allure.step("Получаем информацию о диаграммах и копируемом узле"):
            source_temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            target_diagram_version_id = create_temp_diagram_gen.create_template().versionId
            copying_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
        with allure.step("Копируем узел и получаем идентификатор копии"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=[copying_node_id]).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узел в другую диаграмму"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
            nodes_after_pasting = paste_result.nodes
        with allure.step("Получаем свойства скопированного и вставленного узла"):
            copied_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                                                        copying_node_id).body)
            copied_node_mappings = sorted(copied_node.properties['mappingVariables'],
                                          key=lambda keyval: keyval['typeId'])
            pasted_node_id = list(nodes_after_pasting.keys())[0]
            pasted_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(**get_node_by_id(super_user,
                                                                                                        pasted_node_id).body)
            pasted_node_mappings = sorted(pasted_node.properties['mappingVariables'],
                                          key=lambda keyval: keyval['typeId'])
        with allure.step(
                "Проверяем, что свойства вставленного узла в новой диаграмме совпадают со скопированным"):
            for variable_source, variable_target in zip(copied_node_mappings, pasted_node_mappings):
                assert variable_source['variableName'] == variable_target['variableName']
                assert variable_source['parameter']['parameterName'] == variable_target['parameter']['parameterName']
                assert variable_source['parameter']['parameterId'] != variable_target['parameter']['parameterId']

    @allure.story("При вставке узла завершения в новую диаграмму в список выходных переменных добавляются переменные "
                  "из диаграммы из которой узел был скопирован, а старые переменные остаются")
    @allure.title("Скопировать и вставить узел завершенияв разные диаграммы, проверить, что в списке переменных "
                  "присутствуют как старые так и новые переменные")
    @pytest.mark.smoke
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect",
                             [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.scenario("DEV-6873")
    def test_copypaste_variables_end_node_different_diagram(self, super_user,
                                                            diagram_all_prim_v_one_node_indirect,
                                                            create_temp_diagram_gen):
        with allure.step("Получаем информацию о диаграмме-источнике, копируемом узле; создаем диаграмму-цель"):
            source_temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            source_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            target_diagram_version_id = create_temp_diagram_gen.create_template().versionId
            copying_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            target_execute_status = \
                get_diagram_parameters(super_user, target_diagram_version_id).body["inOutParameters"][0]
        with allure.step("Добавляем в диаграмму-цель одну переменную из диаграммы-источника "
                         "и выходную переменную со случайным именем"):
            target_params_response = update_diagram_parameters(super_user,
                                                               target_diagram_version_id,
                                                               [target_execute_status, source_out_params[0],
                                                                variable_construct(is_execute_status=None,
                                                                                   param_name=generate_string(),
                                                                                   parameter_type="out"
                                                                                   )])
        with allure.step("Копируем узел и получаем идентификатор копии"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=[copying_node_id]).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узел в диаграмму-цель"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
        with allure.step("Получаем переменные диаграммы-цели после вставки"):
            target_params = get_diagram_parameters(super_user, target_diagram_version_id).body["inOutParameters"]
        with allure.step("Проверяем, что после вставки сохранились старые переменные и появились новые"):
            assert len(target_params) == (
                    len(source_out_params) + 2)  # 2 потому что фикстура не возвращает execute_status и мы добавляли еще 1 переменную

    @allure.story("При вставке узла завершения в новую диаграмму входная переменная с идентичным названием становится "
                  "сквозной")
    @allure.title("Скопировать и вставить узел завершения в разные диаграммы, проверить, что в списке переменных "
                  "входная переменная стала сквозной")
    @pytest.mark.smoke
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect",
                             [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.scenario("DEV-6873")
    def test_copypaste_in_out_variable_end_node_different_diagram(self, super_user,
                                                                  diagram_all_prim_v_one_node_indirect,
                                                                  create_temp_diagram_gen):
        with allure.step("Получаем информацию о диаграмме-источнике, копируемом узле; создаем диаграмму-цель"):
            source_temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            source_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            copying_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            target_diagram_version_id = create_temp_diagram_gen.create_template().versionId
            target_execute_status = \
                get_diagram_parameters(super_user, target_diagram_version_id).body["inOutParameters"][0]
        with allure.step("Добавляем выходную переменную диаграммы-источника в диаграмму-цель в качестве входной"):
            target_in_param = source_out_params[0]
            target_in_param.parameterType = ParameterType.IN
            target_params_response = update_diagram_parameters(super_user,
                                                               target_diagram_version_id,
                                                               [target_execute_status, target_in_param])
        with allure.step("Копируем узел и получаем идентификатор копии"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=[copying_node_id]).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узел в диаграмму-цель"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
        with allure.step("Получаем переменные диаграммы-цели после вставки"):
            target_params = get_diagram_parameters(super_user, target_diagram_version_id).body["inOutParameters"]
            checking_variable = [var for var in target_params if var["parameterName"] == target_in_param.parameterName][
                0]  # getting parameter which was in
        with allure.step("Проверяем, что после вставки узла завершения входная переменная стала сквозной и "
                         "кол-во переменных в диаграмме-цели совпадает с кол-вом переменных диаграммы-источника"):
            assert checking_variable["parameterType"] == ParameterType.IN_OUT.value
            assert len(target_params) == (len(source_out_params) + 1)

    @allure.story("При копировании и вставке нескольких узлов в ту же диаграмму, маппинги узлов сохраняются")
    @allure.title("Скопировать и вставить несколько узлов в одной диаграмме и проверить, что маппинги переменных "
                  "остались неизменными")
    @pytest.mark.smoke
    @allure.issue('DEV-18002')
    @pytest.mark.scenario("DEV-6873")
    @pytest.mark.variable_data([VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
                                VariableParams(varName="out_var", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    def test_copypaste_multiple_node_n_link_same_diagram(self, super_user,
                                                         diagram_calc_prim_v,
                                                         create_temp_diagram_gen):
        with allure.step("Получаем информацию о диаграммах и копируемых узлах"):
            source_temp_version_id = diagram_calc_prim_v["diagram_data"].versionId
            target_diagram_version_id = source_temp_version_id
            calc_copying_node_id = diagram_calc_prim_v["calc_node_id"]
            nodes_before_pasting = get_diagram_by_version(super_user,
                                                          source_temp_version_id).body["nodes"]
            source_diagram_nodes = get_diagram_by_version(super_user,
                                                          source_temp_version_id).body["nodes"]
            copying_link_id = source_diagram_nodes[calc_copying_node_id]["outputLinks"][0]
            end_copying_node_id = ''
            # по линку из узла расчета ищем узел завершения
            for node_id, node_property in source_diagram_nodes.items():
                if copying_link_id in (node_property.get('inputLinks') or []):
                    end_copying_node_id = node_id
                    break
            nodes_to_copy = [calc_copying_node_id, end_copying_node_id]
        with allure.step("Копируем узлы и получаем идентификатор copyId"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=nodes_to_copy,
                                                                          link_ids=[copying_link_id]).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узлы в ту же диаграмму"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
            nodes_after_pasting = paste_result.nodes
        with allure.step("Получаем свойства скопированных узлов"):
            calc_copied_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, calc_copying_node_id).body)
            end_copied_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, end_copying_node_id).body)
            # сортируем параметры в узле для последующего сравнения(так как они приходят неотсортированными)
            calc_copied_node_mappings = sorted(calc_copied_node.properties['calculate'],
                                               key=lambda keyval: keyval['rowKey'])
            end_copied_node_mappings = sorted(end_copied_node.properties['mappingVariables'],
                                              key=lambda keyval: keyval['typeId'])
            # так как возвращается целиком вся диаграмма - преобразуем узлы в множества и вычитаем старое из нового
            pasted_node_ids = list(set(nodes_after_pasting.keys()) - set(nodes_before_pasting.keys()))
        with allure.step("Получаем свойства вставленных узлов"):
            first_pasted_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, pasted_node_ids[0]).body)
            second_pasted_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, pasted_node_ids[1]).body)
            if first_pasted_node.nodeTypeId == IntNodeType.varCalc.value:
                calc_pasted_node = first_pasted_node
                end_pasted_node = second_pasted_node
            else:
                calc_pasted_node = second_pasted_node
                end_pasted_node = first_pasted_node
            # сортируем параметры в узле для последующего сравнения(так как они приходят неотсортированными)
            calc_pasted_node_mappings = sorted(calc_pasted_node.properties['calculate'],
                                               key=lambda keyval: keyval['rowKey'])
            end_pasted_node_mappings = sorted(end_pasted_node.properties['mappingVariables'],
                                              key=lambda keyval: keyval['typeId'])
        with allure.step(
                "Проверяем, что свойства вставленного узла в новой диаграмме совпадают со скопированным"):
            assert calc_pasted_node_mappings == calc_copied_node_mappings
            assert end_pasted_node_mappings == end_copied_node_mappings
            assert calc_pasted_node.outputLinks == end_pasted_node.inputLinks and \
                   end_pasted_node.inputLinks != calc_copied_node.outputLinks

    @allure.story("При копировании и вставке нескольких узлов в новую диаграмму, маппинги сохраняются, а "
                  "идентификаторы переменных меняются")
    @allure.title("Скопировать и вставить несколько узлов в разные диаграммы и проверить, что маппинги "
                  "переменных остались неизменными, а идентификаторы выходных переменных изменились")
    @pytest.mark.smoke
    @pytest.mark.scenario("DEV-6873")
    @pytest.mark.variable_data([VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
                                VariableParams(varName="out_var", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["расчет переменной"])
    def test_copypaste_multiple_node_n_link_different_diagram(self, super_user,
                                                              diagram_calc_prim_v,
                                                              create_temp_diagram_gen):
        with allure.step("Получаем информацию о диаграммах и копируемых узлах"):
            source_temp_version_id = diagram_calc_prim_v["diagram_data"].versionId
            target_diagram_version_id = create_temp_diagram_gen.create_template().versionId
            calc_copying_node_id = diagram_calc_prim_v["calc_node_id"]
            source_diagram_nodes = diagram_calc_prim_v["diagram_data"].nodes
            copying_link_id = source_diagram_nodes[calc_copying_node_id]["outputLinks"][0]
            end_copying_node_id = ''
            # по линку из узла расчета ищем узел завершения
            for node_id, node_property in source_diagram_nodes.items():
                if copying_link_id in (node_property.get('inputLinks') or []):
                    end_copying_node_id = node_id
                    break
            nodes_to_copy = [calc_copying_node_id, end_copying_node_id]
        with allure.step("Копируем узлы и получаем идентификатор копии"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=nodes_to_copy,
                                                                          link_ids=[copying_link_id]).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узлы в другую диаграмму"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
            nodes_after_pasting = paste_result.nodes
        with allure.step("Получаем свойства скопированных узлов"):
            calc_copied_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, calc_copying_node_id).body)
            end_copied_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, end_copying_node_id).body)
            # сортируем параметры в узле для последующего сравнения(так как они приходят неотсортированными)
            calc_copied_node_mappings = sorted(calc_copied_node.properties['calculate'],
                                               key=lambda keyval: keyval['rowKey'])
            end_copied_node_mappings = sorted(end_copied_node.properties['mappingVariables'],
                                              key=lambda keyval: keyval['typeId'])
            pasted_node_ids = list(nodes_after_pasting.keys())
        with allure.step("Получаем свойства вставленных узлов"):
            first_pasted_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, pasted_node_ids[0]).body)
            second_pasted_node: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, pasted_node_ids[1]).body)
            if first_pasted_node.nodeTypeId == IntNodeType.varCalc.value:
                calc_pasted_node = first_pasted_node
                end_pasted_node = second_pasted_node
            else:
                calc_pasted_node = second_pasted_node
                end_pasted_node = first_pasted_node
            # сортируем параметры в узле для последующего сравнения(так как они приходят неотсортированными)
            calc_pasted_node_mappings = sorted(calc_pasted_node.properties['calculate'],
                                               key=lambda keyval: keyval['rowKey'])
            end_pasted_node_mappings = sorted(end_pasted_node.properties['mappingVariables'],
                                              key=lambda keyval: keyval['typeId'])
        with allure.step("Сравниваем свойства вставленных узлов и скопированных"):
            for variable_source, variable_target in zip(end_copied_node_mappings, end_pasted_node_mappings):
                assert variable_source['variableName'] == variable_target['variableName']
                assert variable_source['parameter']['parameterName'] == variable_target['parameter']['parameterName']
                assert variable_source['parameter']['parameterId'] != variable_target['parameter']['parameterId']
            assert calc_copied_node_mappings == calc_pasted_node_mappings
            assert calc_pasted_node.outputLinks == end_pasted_node.inputLinks and \
                   end_pasted_node.inputLinks != calc_copied_node.outputLinks

    @allure.story("При копировании и вставке узла ветвления со всеми ветвями, вставленный узел сохраняет настройки")
    @allure.title("Скопировать и вставить узел ветвления со всеми узлами к которым есть связь от него, проверить "
                  "что настройки узла ветвления совпадают с первоначальными")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_copypaste_branch_node_all_branches(self, super_user, diagram_branch_saved):
        with allure.step("Получаем информацию о диаграмме и узле"):
            source_temp_version_id = diagram_branch_saved["temp_version_id"]
            target_diagram_version_id = source_temp_version_id
            nodes_before_pasting = get_diagram_by_version(super_user, source_temp_version_id).body["nodes"]

            copying_branch_node_id = diagram_branch_saved["diagram_nodes"]["Ветвление"].nodeId
            copying_end1_node_id = diagram_branch_saved["diagram_nodes"]["завершение"].nodeId
            copying_end2_node_id = diagram_branch_saved["diagram_nodes"]["завершение_1"].nodeId
            copying_link1_id = diagram_branch_saved["diagram_links"]["Ветвление->Завершение"]
            copying_link2_id = diagram_branch_saved["diagram_links"]["Ветвление->Завершение_1"]
            copying_nodes = [copying_branch_node_id, copying_end1_node_id, copying_end2_node_id]
            copying_links = [copying_link1_id, copying_link2_id]
        with allure.step("Копируем узлы и получаем идентификатор копии"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=copying_nodes,
                                                                          link_ids=copying_links).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узлы в ту же диаграмму"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
            nodes_after_pasting = paste_result.nodes
            pasted_node_ids = list(set(nodes_after_pasting.keys()) - set(nodes_before_pasting.keys()))
        with allure.step("Получаем свойства вставленного узла ветвления и скопированного"):
            pasted_branch_node = None
            for node_id in pasted_node_ids:
                node = get_node_by_id(super_user, node_id).body
                if node["nodeTypeId"] == IntNodeType.branch.value:
                    pasted_branch_node = NodeViewWithVariablesDto.construct(**node)
                    break
            copying_branch_node = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, copying_branch_node_id).body)
        with allure.step("Проверяем, что ветви и значения для ветвления совпали с копируемым узлом"):
            assert pasted_branch_node.properties["branches"][0]["nodeId"] in pasted_node_ids \
                   and pasted_branch_node.properties["defaultPath"]["nodeId"] in pasted_node_ids, "no path node"
            assert pasted_branch_node.properties["branches"][0]["valueFrom"] == \
                   copying_branch_node.properties["branches"][0]["valueFrom"] \
                   and pasted_branch_node.properties["branches"][0]["operator"] == \
                   copying_branch_node.properties["branches"][0]["operator"], "wrong operator or value"

    @allure.story("При копировании и вставке узла ветвления с одной ветвью, вставленный узел сохраняет настройки")
    @allure.title("Скопировать и вставить узел ветвления с одним узлом с которым есть связь от него, проверить "
                  "что настройки узла ветвления совпадают с начальными по 1 ветви, а вторая ветвь отсутствует")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    def test_copypaste_branch_node_single_branch(self, super_user, diagram_branch_saved):
        with allure.step("Получаем информацию о диаграмме и узле"):
            source_temp_version_id = diagram_branch_saved["temp_version_id"]
            target_diagram_version_id = source_temp_version_id
            nodes_before_pasting = get_diagram_by_version(super_user, source_temp_version_id).body["nodes"]

            copying_branch_node_id = diagram_branch_saved["diagram_nodes"]["Ветвление"].nodeId
            copying_end1_node_id = diagram_branch_saved["diagram_nodes"]["завершение"].nodeId
            copying_link1_id = diagram_branch_saved["diagram_links"]["Ветвление->Завершение"]
            copying_nodes = [copying_branch_node_id, copying_end1_node_id]
            copying_links = [copying_link1_id]
        with allure.step("Копируем узлы и получаем идентификатор копии"):
            copy_result: ResponseDto = ResponseDto.construct(**copy_nodes(super_user,
                                                                          version_id=source_temp_version_id,
                                                                          node_ids=copying_nodes,
                                                                          link_ids=copying_links).body)
            copy_id = copy_result.uuid
        with allure.step("Вставляем узлы в ту же диаграмму"):
            paste_result: DiagramViewDto = DiagramViewDto.construct(**paste_nodes(super_user,
                                                                                  copy_id=copy_id,
                                                                                  version_id=target_diagram_version_id).body["diagram"])
            nodes_after_pasting = paste_result.nodes
            pasted_node_ids = list(set(nodes_after_pasting.keys()) - set(nodes_before_pasting.keys()))
        with allure.step("Получаем свойства вставленного узла ветвления и скопированного"):
            pasted_branch_node = None
            for node_id in pasted_node_ids:
                node = get_node_by_id(super_user, node_id).body
                if node["nodeTypeId"] == IntNodeType.branch.value:
                    pasted_branch_node = NodeViewWithVariablesDto.construct(**node)
                    break
            copying_branch_node = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, copying_branch_node_id).body)
        with allure.step("Проверяем, что ветви и значения для ветвления совпали с копируемым узлом, а "
                         "на ветви по-умолчанию нет нескопированного узла"):
            assert pasted_branch_node.properties["branches"][0]["nodeId"] in pasted_node_ids \
                   and pasted_branch_node.properties["defaultPath"]["nodeId"] is None, "no path node"
            assert pasted_branch_node.properties["branches"][0]["valueFrom"] == \
                   copying_branch_node.properties["branches"][0]["valueFrom"] \
                   and pasted_branch_node.properties["branches"][0]["operator"] == \
                   copying_branch_node.properties["branches"][0]["operator"], "wrong operator or value"