import glamor as allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import (
    DiagramInOutParameterFullViewDto,
    DiagramInOutParametersViewDto,
    NodeViewWithVariablesDto, NodeValidateDto, ResponseDto, DiagramCreateNewVersion, NodeUpdateDto,
)
from products.Decision.framework.steps.decision_steps_diagram import validate_diagram, update_diagram_parameters, \
    save_diagram
from products.Decision.framework.steps.decision_steps_nodes import (
    update_node,
    get_node_by_id, automap_node, validate_node,
)
from products.Decision.utilities.custom_models import VariableParams, IntValueType
from products.Decision.utilities.custom_type_constructors import attribute_construct
from products.Decision.utilities.node_cunstructors import (
    variables_for_node,
    node_update_construct,
)


@allure.epic("Диаграммы")
@allure.feature("Узел завершения")
class TestFinishNode:
    @allure.story("Нет ошибок, если узел корректно заполнен")
    @allure.title("Создаем диаграмму с корректно заполненным узлом завершения")
    @pytest.mark.scenario("DEV-15455")
    @pytest.mark.parametrize("is_null, valid", [(True, True), (False, False)])
    @pytest.mark.smoke
    def test_node_finish(self, super_user, diagram_for_finish, is_null, valid):
        with allure.step(
                "Создание временной версии диаграммы с заданными двумя переменными "
                "(одна на вход, вторая на выход), задаем узлы и связи между ними,"
                "получаем id узла завершения и имена переменных"
        ):
            template: DiagramInOutParametersViewDto = (
                DiagramInOutParametersViewDto.construct(
                    **diagram_for_finish["template"]
                )
            )
            node_finish_id = diagram_for_finish["node_finish_id"]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_for_finish[
                "diagram_param_out"
            ]

        with allure.step("Обновление узла завершения без маппинга"):
            finish_variable = variables_for_node(
                node_type="finish_out",
                is_arr=False,
                is_compl=False,
                name="",
                vers_id=diagram_param_out.parameterId,
                type_id=1,
                param_name=diagram_param_out.parameterName,
                is_null_value=is_null,
            )
            node_finish_upd = node_update_construct(
                714, 202.22915649414062, "finish", template.versionId, [finish_variable]
            )

            update_node(super_user, node_id=node_finish_id, body=node_finish_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_finish_upd.nodeTypeId,
                            properties=node_finish_upd.properties))
        with allure.step("Получение информации об узле завершения"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_finish_id).body
            )
        with allure.step("валидируем, view.validFlag соответствует значению is_null"):
            assert node_view.validFlag == valid

    @allure.story(
        "Предусмотрена проверка на то, что переменные блока завершения соответствуют"
        " переменным диаграммы с признаком выходного параметра"
    )
    @allure.title(
        "Создаем диаграмму с двумя переменными, в узле завершения произвести "
        "маппинг входной переменной на выходную"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.smoke
    def test_node_finish_mapping_inp_var(self, super_user, diagram_for_finish):
        with allure.step(
                "Создание временной версии диаграммы с заданными двумя переменными "
                "(одна на вход, вторая на выход), задаем узлы и связи между ними,"
                "получаем id узла завершения и имена переменных"
        ):
            template: DiagramInOutParametersViewDto = (
                DiagramInOutParametersViewDto.construct(
                    **diagram_for_finish["template"]
                )
            )
            temp_version_id = diagram_for_finish["template"]["versionId"]
            node_finish_id = diagram_for_finish["node_finish_id"]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_for_finish[
                "diagram_param_out"
            ]
            diagram_param_inp: DiagramInOutParameterFullViewDto = diagram_for_finish[
                "diagram_param_inp"
            ]
        with allure.step("Обновление узла завершения с маппингом"):
            finish_variable = variables_for_node(
                node_type="finish_out",
                is_arr=False,
                is_compl=False,
                name=diagram_param_inp.parameterName,
                vers_id=diagram_param_out.parameterId,
                type_id=1,
                param_name=diagram_param_out.parameterName,
                is_null_value=False,
            )

            node_finish_upd = node_update_construct(
                714, 202.22915649414062, "finish", template.versionId, [finish_variable]
            )

            update_node(super_user, node_id=node_finish_id, body=node_finish_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_finish_upd.nodeTypeId,
                            properties=node_finish_upd.properties))

        with allure.step("Валидируем что нет ошибки"):
            validate = validate_diagram(super_user, temp_version_id)
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_finish_id).body
            )
            assert (
                    validate.body["httpCode"] == 200
                    and validate.body["operation"] == "validate"
                    and node_view.validFlag
            )

    @allure.story(
        "Нет ошибки, если на выходные переменные намаплена одна и та же переменная"
    )
    @allure.title(
        "Создаем диаграмму с двумя переменными, в узле завершения произвести "
        "маппинг входной переменной на выходные"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.smoke
    def test_node_finish_mapping_inp_var2(self, super_user, diagram_for_finish_two_var):
        with allure.step(
                "Создание временной версии диаграммы с заданными тремя переменными "
                "(одна на вход, две на выход), задаем узлы и связи между ними,"
                "получаем id узла завершения и имена переменных"
        ):
            template: DiagramInOutParametersViewDto = (
                DiagramInOutParametersViewDto.construct(
                    **diagram_for_finish_two_var["template"]
                )
            )
            temp_version_id = diagram_for_finish_two_var["template"]["versionId"]
            node_finish_id = diagram_for_finish_two_var["node_finish_id"]
            diagram_param_out2: DiagramInOutParameterFullViewDto = diagram_for_finish_two_var[
                "diagram_param_out2"
            ]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_for_finish_two_var[
                "diagram_param_out"
            ]
            diagram_param_inp: DiagramInOutParameterFullViewDto = diagram_for_finish_two_var[
                "diagram_param_inp"
            ]
        with allure.step(
                "Обновление узла завершения на выходные переменные намаппливаем одну и ту же входную"
        ):
            finish_variable = variables_for_node(
                node_type="finish_out",
                is_arr=False,
                is_compl=False,
                name=diagram_param_inp.parameterName,
                vers_id=diagram_param_out.parameterId,
                type_id=1,
                param_name=diagram_param_out.parameterName,
                is_null_value=False,
            )
            finish_variable2 = variables_for_node(
                node_type="finish_out",
                is_arr=False,
                is_compl=False,
                name=diagram_param_inp.parameterName,
                vers_id=diagram_param_out2.parameterId,
                type_id=1,
                param_name=diagram_param_out2.parameterName,
                is_null_value=False,
            )
            node_finish_upd = node_update_construct(
                714,
                202.22915649414062,
                "finish",
                template.versionId,
                [finish_variable, finish_variable2],
            )

            update_node(super_user, node_id=node_finish_id, body=node_finish_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_finish_upd.nodeTypeId,
                            properties=node_finish_upd.properties))

        with allure.step("Проверяем что валидация диаграммы с намапплиной одной переменной на две "
                         "выходные прошла успешно"):
            validate = validate_diagram(super_user, temp_version_id)
            assert (
                    validate.body["httpCode"] == 200
                    and validate.body["operation"] == "validate"
            )

    @allure.story(
        "Предусмотрена проверка на то, что элементы блока завершения напамплены"
        " на переменные диаграммы, если не отжат флаг Null значение"
    )
    @allure.title("Передаём значение в узел завершения с включённым флагом null значения")
    @pytest.mark.scenario("DEV-6398")
    @allure.issue(url="DEV-9613")
    @allure.issue(url="DEV-10470")
    @pytest.mark.smoke
    def test_node_finish_null_true(self, super_user, diagram_for_finish):
        with allure.step(
                "Создание временной версии диаграммы с заданными двумя переменными "
                "(одна на вход, одна на выход), задаем узлы и связи между ними,"
                "получаем id узла завершения и имена переменных"
        ):
            template: DiagramInOutParametersViewDto = (
                DiagramInOutParametersViewDto.construct(
                    **diagram_for_finish["template"]
                )
            )
            node_finish_id = diagram_for_finish["node_finish_id"]
            temp_version_id = diagram_for_finish["template"]["versionId"]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_for_finish[
                "diagram_param_out"
            ]
            diagram_param_inp: DiagramInOutParameterFullViewDto = diagram_for_finish[
                "diagram_param_inp"
            ]

        with allure.step(
                "Обновление узла завершения намапливаем переменную и проставляем флаг is_null_value = True"
        ):
            finish_variable = variables_for_node(
                node_type="finish_out",
                is_arr=False,
                is_compl=False,
                name=diagram_param_inp.parameterName,
                vers_id=diagram_param_out.parameterId,
                type_id=1,
                param_name=diagram_param_out.parameterName,
                is_null_value=True,
                param_id=diagram_param_inp.parameterId
            )
            node_finish_upd = node_update_construct(
                714, 202.22915649414062, "finish", template.versionId, [finish_variable]
            )

            update_node(super_user, node_id=node_finish_id, body=node_finish_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_finish_upd.nodeTypeId,
                            properties=node_finish_upd.properties))

        with allure.step("Ожидаем ошибку так как флаг is_null_value = True, приходит 200. "):
            with pytest.raises(HTTPError):
                assert validate_diagram(super_user, temp_version_id).body["httpCode"] == 422

    @allure.story("Состав переменных узла завершения обновляется при изменении состава выходных переменных диаграммы")
    @allure.title("Создать диаграмму с параметрами всех типов, убрать параметр из выходных параметров, проверить, что"
                  "в переменных узла завершения параметров стало меньше")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variable_end_node_auto_updating(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Формирование обновленного состава переменных диаграммы"):
            new_all_params = all_in_params + all_out_params[:-1] + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
            end_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что количество переменных пришедших в центральный узел с обеих сторон совпадает с "
                         "количеством переменных диаграммы"):
            assert len(end_node_view.properties["mappingVariables"]) == len(all_out_params) - 1

    @allure.story("Маппинг узла завершения сохраняется после обновления состава переменных диаграммы")
    @allure.title("Создать диаграмму с параметрами всех типов, вызвать put /parameters проверить, что узел завершения "
                  "соответствует начальному")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.skip("need fix")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_end_node_mapping_not_changing(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Первичное получение узла"):
            first_end_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Формирование обновленного состава переменных диаграммы"):
            new_all_params = all_in_params + all_out_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
        with allure.step("Повторное получение узла"):
            second_end_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Сортировка переменных узлов перед сравнением"):
            first_end_node_sorted_varibles = sorted(first_end_node_view.properties["mappingVariables"],
                                                    key=lambda keyval: keyval['typeId'])
            second_end_node_sorted_varibles = sorted(second_end_node_view.properties["mappingVariables"],
                                                     key=lambda keyval: keyval['typeId'])
        with allure.step("Проверка что маппинги при первичном получении узла и после обновления параметров совпали"):
            assert first_end_node_sorted_varibles == \
                   second_end_node_sorted_varibles

    @allure.story("При изменении флага массива в переменной на выход, флаг меняется в узле завершения")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг массива на переменных на выход, "
                  "проверить что сменился в переменных узла завершения ")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_end_node_array_flag_changing(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            flag_on_the_start = all_out_params[0].arrayFlag
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Смена флагов выходных переменных на массивы и обновление состава переменных диаграммы"):
            for variable in all_out_params:
                variable.arrayFlag = not variable.arrayFlag
            new_all_params = all_in_params + all_out_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что все переменные центрального узла изменили флаг"):
            for output_variable in param_check_node_view.properties["mappingVariables"]:
                assert output_variable["isArray"] is not flag_on_the_start

    @allure.story("При изменении типа выходной переменной на комплексный - тип и флаг меняются в узле завершения")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг и тип на выходных переменных, "
                  "проверить что сменился в переменных узла завершения")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_end_node_ctype_flag_changing(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                    create_custom_types_gen):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Создание комплексного типа"):
            ctype_name = "attr_" + generate_string()
            create_response: ResponseDto = create_custom_types_gen.create_type(ctype_name, [attribute_construct()])
            ctype_version_id = create_response.uuid
        with allure.step("Смена флагов и типов выходных переменных на комплексные и обновление переменных диаграммы"):
            for variable in all_out_params:
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
            for output_variable in param_check_node_view.properties["mappingVariables"]:
                assert output_variable["isComplex"] and output_variable["typeId"] == ctype_version_id

    @allure.story("При изменении типа выходной переменной на справочник - флаг и dictId меняются в узле завершения")
    @allure.title(
        "Создать диаграмму с параметрами всех типов, поменять флаг и добавтить dictId на выходных переменных, "
        "проверить что сменился в узле завершения")
    @pytest.mark.scenario("DEV-5811")
    @pytest.mark.dict_types(["all_types"])
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_end_node_dict_flag_changing(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                   create_custom_custom_attributes):
        with allure.step("Получение переменных диаграммы и идентификаторов справочников"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
            dicts = create_custom_custom_attributes
        with allure.step("Смена флагов и типов выходных переменных и обновление переменных диаграммы"):
            for variable in all_out_params:
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
            for output_variable in param_check_node_view.properties["mappingVariables"]:
                assert output_variable["isDict"] and output_variable["dictId"] == dicts[output_variable["typeId"]].id

    # @allure.story("Предусмотрена проверка того, что пользовательский тип, атрибут которого"
    #               "намаплен на элемент блока завершения, существует")
    # @allure.title("Создаем диаграмму с пользовательским типом переменной на вход и интовой на выход"
    #               "производим маппинг атрибута пользовательского типа переменной на выходную переменную"
    #               " узла завершения")
