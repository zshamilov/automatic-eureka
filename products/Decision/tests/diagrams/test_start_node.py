import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import DiagramInOutParametersViewDto, DiagramInOutParameterFullViewDto, \
    NodeViewWithVariablesDto, ResponseDto, NodeValidateDto
from products.Decision.framework.steps.decision_steps_diagram import update_diagram_parameters
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id, create_node
from products.Decision.utilities.custom_type_constructors import attribute_construct
from products.Decision.utilities.node_cunstructors import node_update_construct, variables_for_node, node_construct


@allure.epic("Диаграммы")
@allure.feature("Узел начала")
class TestDiagramsStartNode:
    @allure.story("Предусмотрена проверка на то, что переменные, указанные в блоке соответствуют"
                  " переменным в таблице diagram_in_out_parameter, у которых "
                  "parameter_type = 'IN' или 'IN_OUT'")
    @allure.title(
        "Создать диаграмму С двумя переменными, одна на вход, вторая на выход и вход,"
        " проверить что в узле начала есть обе переменные"
    )
    @pytest.mark.scenario("DEV-15452")
    @pytest.mark.smoke
    def test_node_start(self, super_user, diagram_for_start):
        found_vars = 0
        with allure.step("Создание временной версии диаграммы с заданными двумя переменными"
                         "(одна на вход, вторая на вход и выход), задаем узлы и связи между ними,"
                         "получаем id узла Начало и имена переменных"):
            template: DiagramInOutParametersViewDto = DiagramInOutParametersViewDto.construct(
                **diagram_for_start["template"])
            node_start_id = diagram_for_start["node_start_id"]
            temp_version_id = diagram_for_start["template"]["versionId"]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_for_start["diagram_param_out"]
            diagram_param_inp: DiagramInOutParameterFullViewDto = diagram_for_start["diagram_param_inp"]

        with allure.step("Обновление узла начала"):
            start_variable = variables_for_node(node_type="start", is_arr=False, is_compl=False,
                                                name=diagram_param_inp.parameterName,
                                                vers_id=diagram_param_inp.parameterId,
                                                type_id=1)
            start_variable2 = variables_for_node(node_type="start", is_arr=False, is_compl=False,
                                                 name=diagram_param_out.parameterName,
                                                 vers_id=diagram_param_out.parameterId,
                                                 type_id=1)
            node_start_upd = node_update_construct(714, 202.22915649414062, "start",
                                                   template.versionId,
                                                   [start_variable, start_variable2])

            update_node(super_user, node_id=node_start_id, body=node_start_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_start_upd.nodeTypeId,
                            properties=node_start_upd.properties))

        with allure.step("Получение информации об узле по id"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_start_id).body
            )
            for var in node_view.properties["mappingVariables"]:
                if var["variableName"] == diagram_param_inp.parameterName:
                    found_vars += 1
                if var["variableName"] == diagram_param_out.parameterName:
                    found_vars += 1

        with allure.step("Проверяем что в маппинге узла Начало обе созданные переменные"):
            assert found_vars == 2

    @allure.story("При создании пустого узла начала, происходит автозаполнение на входные переменные")
    @allure.title("При создании пустого узла начала, происходит автозаполнение на входные переменные")
    @pytest.mark.scenario("DEV-15452")
    @pytest.mark.smoke
    def test_node_start_autocomplete(self, super_user,
                                     create_temp_with_in_out_v):
        template = create_temp_with_in_out_v["template"]
        diagram_param: DiagramInOutParameterFullViewDto = create_temp_with_in_out_v["diagram_param"]
        temp_version_id = template.versionId
        node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id)
        node_start_id = ResponseDto.construct(
            **create_node(super_user, node_start_raw).body).uuid
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_start_id).body
        )
        assert node_view.properties["mappingVariables"][0]["parameterId"] == diagram_param.parameterId

    @allure.story("Состав переменных узла начала обновляется при изменении состава входных переменных диаграммы")
    @allure.title("Создать диаграмму с параметрами всех типов, убрать параметр из входных параметров, проверить, что"
                  "в переменных узла начала параметров стало меньше")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variable_end_node_auto_updating(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_start_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Формирование обновленного состава переменных диаграммы"):
            new_all_params = all_in_params[:-1] + all_out_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
            start_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что количество переменных пришедших в центральный узел с обеих сторон совпадает с "
                         "количеством переменных диаграммы"):
            assert len(start_node_view.properties["mappingVariables"]) == len(all_in_params) - 1

    @allure.story("При изменении флага массива в переменной на вход, флаг меняется в узле начала")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг на переменных на вход, "
                  "проверить что сменился в узле начала")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_start_node_array_flag_changing(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_start_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            flag_on_the_start = diagram_all_prim_v_one_node_indirect["array_flag"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Смена флагов переменных и обновление переменных"):
            for variable in all_in_params:
                variable.arrayFlag = not variable.arrayFlag
            new_all_params = all_in_params + all_out_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что все переменные центрального узла изменили флаг"):
            for input_variable in param_check_node_view.properties["mappingVariables"]:
                assert input_variable["isArray"] is not flag_on_the_start

    @allure.story("При изменении типа выходной переменной на комплексный - тип и флаг меняются в узле начала")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг и тип на входных переменных, "
                  "проверить что сменился в переменных узла начала")
    @pytest.mark.scenario("DEV-5811")
    @allure.link("DEV-5811")
    @pytest.mark.smoke
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    def test_variables_start_node_ctype_flag_changing(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                      create_custom_types_gen):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_start_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Создание комплексного типа"):
            ctype_name = "attr_" + generate_string()
            create_response: ResponseDto = create_custom_types_gen.create_type(ctype_name, [attribute_construct()])
            ctype_version_id = create_response.uuid
        with allure.step("Смена флагов и типов выходных переменных и обновление переменных диаграммы"):
            for variable in all_in_params:
                variable.complexFlag = True
                variable.typeId = ctype_version_id
            new_all_params = all_in_params + all_out_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что все переменные центрального узла изменили флаг"):
            for input_variable in param_check_node_view.properties["mappingVariables"]:
                assert input_variable["isComplex"] and input_variable["typeId"] == ctype_version_id

    @allure.story("При изменении типа выходной переменной на справочник - флаг и dictId меняются в узле начала")
    @allure.title(
        "Создать диаграмму с параметрами всех типов, поменять флаг и добавтить dictId на входных переменных, "
        "проверить что сменился в узле начала")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.dict_types(["all_types"])
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_start_node_dict_flag_changing(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                     create_custom_custom_attributes):
        with allure.step("Получение переменных диаграммы и идентификаторов справочников"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_start_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
            dicts = create_custom_custom_attributes
        with allure.step("Смена флагов и типов выходных переменных и обновление переменных диаграммы"):
            for variable in all_in_params:
                variable.dictFlag = True
                variable.dictId = dicts[str(variable.typeId)].id
                variable.dictName = str(variable.typeId)
            new_all_params = all_in_params + all_out_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что все переменные центрального узла изменили флаг"):
            for input_variable in param_check_node_view.properties["mappingVariables"]:
                assert input_variable["isDict"] and input_variable["dictId"] == dicts[input_variable["typeId"]].id
