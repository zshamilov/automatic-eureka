import glamor as allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import (
    ResponseDto,
    NodeViewWithVariablesDto,
    DiagramViewDto,
    NodeViewShortInfo,
    ComplexTypeGetFullView,
    DiagramInOutParameterFullViewDto,
    NodeValidateDto, AttributeShortView, )
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version,
)
from products.Decision.framework.steps.decision_steps_nodes import (
    create_node,
    update_node,
    get_node_by_id,
)
from products.Decision.utilities.custom_models import VariableParams, BasicPrimitiveValues
from products.Decision.utilities.node_cunstructors import (
    node_update_construct,
    node_construct,
    variables_for_node,
)


@allure.epic("Диаграммы")
@allure.feature("Узел расчета переменных")
class TestDiagramsVariableCalculationNode:
    @allure.story(
        "В качестве переменной можно подать входную переменную и пересчитать ей значение всех примитивных "
        "типов"
    )
    @allure.title(
        "Обновить узел рассчёта переменных добавив входной примитив параметр с пересчитанным значением"
    )
    @pytest.mark.scenario("DEV-15456")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.parametrize("param, value", [("in_int_param", "1"),
                                              ("in_float_param", "1.0"),
                                              ("in_str_param", "'some_string'"),
                                              ("in_date_param", "'2023-04-23'"),
                                              ("in_bool_param", "true"),
                                              ("in_date_time_param", "'2023-04-24 17:06:13'"),
                                              ("in_time_param", "'09:00:00'")])
    @allure.issue("DEV-12972")
    @pytest.mark.smoke
    def test_create_node_var_calc_with_input(
            self,
            super_user,
            diagram_all_prim_v_one_node_indirect, param, value
    ):
        with allure.step("Создание диаграммы с узлами для обновления"):
            node_calc_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            diagram_id = diagram_all_prim_v_one_node_indirect["diagram_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect[param]
        with allure.step("Обновление узла рассчёта"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=False,
                is_compl=False,
                name=param.parameterName,
                type_id=param.typeId,
                vers_id=None,
                calc_val=value,
                calc_type_id="2",
                param_id=param.parameterId
            )

            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                temp_version_id,
                [node_calc_vars],
                diagram_id=diagram_id
            )
            update_node(super_user, node_id=node_calc_id, body=node_calc_upd)
        with allure.step("Получение информации об узле рассчёта"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_calc_id).body
            )
        with allure.step("Проверка, что значение параметра корректно"):
            assert (
                    node_view.properties["calculate"][0]["expression"][
                        "calculateExpressionValue"] == value and node_view.validFlag
            )

    @allure.story("Узел можно создать с NodeType = 6")
    @allure.title(
        "Создать диаграмму с узлом рассчёта переменных без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15456")
    @pytest.mark.smoke
    def test_create_node_var_calc(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла рассчёта переменных"):
            node_calc = node_construct(
                700, 202.22915649414062, "var_calc", template["versionId"], None
            )
            node_calc_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_calc).body
            )
            node_calc_id = node_calc_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла рассчёта корректен и равен 6"
        ):
            assert diagram.nodes[str(node_calc_id)].nodeTypeId == 6

    @allure.story(
        "В качестве переменной можно создать переменную всех примитивных типов внутри узла рассчёта и "
        "выставить ей значение"
    )
    @allure.title(
        "Создать диаграмму с узлом рассчёта переменных с примитивным атрибутом, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15456")
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.parametrize("array", [False, True])
    @pytest.mark.parametrize(
        "prim_type, calc_val, valid",
        [
            ("0", BasicPrimitiveValues.floatBasic.value, True),
            ("1", BasicPrimitiveValues.intBasic.value, True),
            ("2", BasicPrimitiveValues.strBasic.value, True),
            ("3", "'2021-11-22'", True),
            ("4", BasicPrimitiveValues.boolBasic.value, True),
            ("5", "'2021-11-22 15:15:45.000'", True),
            ("6", "'15:15:45'", True),
            ("7", BasicPrimitiveValues.longBasic.value, True)
        ]
    )
    def test_create_node_var_calc_with_prim_attr(
            self, super_user, diagram_constructor, array, prim_type, calc_val, valid
    ):
        if array:
            if prim_type == "2" or prim_type == "4":
                calc_val = f"['{calc_val}']"
            else:
                calc_val = f"[{calc_val}]"
        else:
            if prim_type == "2" or prim_type == "4":
                calc_val = f"'{calc_val}'"

        with allure.step("Создание template диаграммы"):
            temp_version_id = diagram_constructor["temp_version_id"]
            node_calc_id = diagram_constructor["nodes"]["расчет переменной"].nodeId
        with allure.step("Обновление узла рассчёта на различные примитив параметры"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=array,
                is_compl=False,
                name="node_attribute",
                type_id=int(prim_type),
                vers_id=None,
                calc_val=str(calc_val),
                calc_type_id=prim_type
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                temp_version_id,
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc_id, body=node_calc_upd)
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_calc_id).body
            )
        with allure.step("Проверка, что атрибут валиден и добавлен"):
            assert (
                    node_view.validFlag == valid
                    and any(v["variableName"] == "node_attribute" for v in node_view.availableToCalc) == 1
                    and node_view.validationPayload is None
            )

    @allure.story(
        "В качестве значения возможно подать один из элементов комплексного типа(примитивный тип которого "
        "соответствует типу расчитываемой переменной). Знак $ перед переменной"
    )
    @allure.title(
        "В качестве атрибута узла взять примитив, лежащий внутри входного комплекс типа и пересчитать ему значение"
    )
    @pytest.mark.scenario("DEV-15456")
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx",
                                               varType="in", isComplex=True, isArray=False),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["расчет переменной"])
    @allure.issue("DEV-9588")
    @pytest.mark.smoke
    def test_create_node_compl_var_calc(
            self,
            super_user,
            diagram_constructor
    ):
        input_var_check = False
        with allure.step("Создание диаграммы и комплекс типов"):
            template: DiagramViewDto = diagram_constructor["diagram_info"]
            node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
            node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
            node_calc_id = node_calc.nodeId
        with allure.step("Обновление узла на атрибут лежащий внутри комплекс типа"):
            node_calc_vars = variables_for_node(
                node_type="var_calc",
                is_arr=False,
                is_compl=False,
                name=attr.attributeName,
                type_id=attr.primitiveTypeId,
                calc_val="3",
                calc_type_id=attr.primitiveTypeId,
                var_path=param.parameterName,
                var_root_id=param.typeId,
                param_id=param.parameterId
            )
            node_calc_upd = node_update_construct(
                700,
                202.22915649414062,
                "var_calc",
                template.versionId,
                [node_calc_vars],
            )
            update_node(super_user, node_id=node_calc_id, body=node_calc_upd)
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_calc_id).body
            )
            node_end_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_end.nodeId).body
            )
            for inp_var in node_end_view.availableToCalc:
                if inp_var["variableName"] == param.parameterName:
                    input_var_check = True
                    break
        with allure.step("Проверка. что атрибут добавлен и его название корректно"):
            assert (
                    input_var_check
                    and any(var["variableName"] == attr.attributeName for var in node_view.availableToCalc)
            )

    @allure.story(
        "В качестве значения возможно подать обычную переменную. Знак $ перед переменной"
    )
    @allure.title("В значение атрибута узла подставить значение другого атрибута узла")
    @pytest.mark.scenario("DEV-15456")
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx",
                                               varType="in", isComplex=True, isArray=False),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_create_node_int_var_recalc_on_compl(
            self,
            super_user,
            create_temp_diagram,
            diagram_constructor,
    ):
        template: DiagramViewDto = diagram_constructor["diagram_info"]
        param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
        complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
        attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
        node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        node_calc_id = node_calc.nodeId
        node_calc_vars = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name=attr.attributeName,
            type_id=attr.primitiveTypeId,
            vers_id=None,
            calc_val="3",
            calc_type_id=attr.primitiveTypeId,
            var_path=param.parameterName,
            var_root_id=param.typeId,
            param_id=param.parameterId
        )
        node_calc_upd = node_update_construct(
            700, 202.22915649414062, "var_calc", template.versionId, [node_calc_vars]
        )
        update_node(super_user, node_id=node_calc_id, body=node_calc_upd)
        node_calc_vars1 = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name="new_attr",
            type_id="1",
            vers_id=None,
            calc_val=f"${param.parameterName}.{attr.attributeName}",
            calc_type_id="1"
        )
        node_calc_upd1 = node_update_construct(
            700,
            202.22915649414062,
            "var_calc",
            template.versionId,
            [node_calc_vars1, node_calc_vars],
        )
        update_node(super_user, node_id=node_calc_id, body=node_calc_upd1)

        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_calc_id).body
        )

        assert any(
            prop["expression"]["calculateExpressionValue"] == f"${param.parameterName}.{attr.attributeName}"
            for prop in node_view.properties["calculate"]
        )

    @allure.story(
        "Недопустимо рассчитывать переменную ещё не рассчитанную в узле расчёта"
    )
    @allure.title(
        "В качестве аргумента переменной - функции подать значение другой переменной узла, определённую в этом же узле"
    )
    @pytest.mark.skip("устарело из-за добавления валидации expression editor")
    @pytest.mark.scenario("DEV-6398")
    def test_node_calc_values_func_prim_neg(self, super_user, create_temp_diagram):
        template = create_temp_diagram
        node_calc = node_construct(
            700, 202.22915649414062, "var_calc", template["versionId"], None
        )
        node_calc_response: ResponseDto = ResponseDto.construct(
            **create_node(super_user, node_calc).body
        )
        node_calc_id = node_calc_response.uuid
        var_name = "new_var"
        node_calc_vars = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name=var_name,
            type_id="2",
            vers_id=None,
            calc_val="\"aaaa\"",
            calc_type_id="2"
        )
        node_calc_upd = node_update_construct(
            700, 202.22915649414062, "var_calc", template["versionId"], [node_calc_vars]
        )
        update_node(super_user, node_id=node_calc_id, body=node_calc_upd)
        node_calc_vars1 = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name="new_func",
            type_id="2",
            calc_val=f"lower(${var_name})",
            calc_type_id="2",
            func_ids=["30"]
        )
        node_calc_upd1 = node_update_construct(
            700,
            202.22915649414062,
            "var_calc",
            template["versionId"],
            [node_calc_vars1, node_calc_vars],
        )
        update_node(super_user, node_id=node_calc_id, body=node_calc_upd1)

        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_calc_id).body
        )
        assert not node_view.validFlag
        assert node_view.validationPayload["nodeValidationMap"]["calculate"][node_calc_vars1.rowKey]["expression"] \
               == "Ошибка в процессе выполнения скрипта: null"
        assert len(node_view.validationPayload["nodeValidationMap"]["calculate"].keys()) == 1

    @allure.story(
        "В качестве значения возможно подать все функции из таблицы-справочника function из БД, в которых в "
        "качестве значения переменных возможно указать как прописанные элементы, так и расчитанные "
        "переменные. Знак $ перед переменной."
    )
    @pytest.mark.scenario("DEV-15456")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.parametrize("func, type_id, param_name, func_id", [("exp($in_int_v)", 0, "in_int_v", "21"),
                                                                    ("log2($in_float_v)", 0, "in_float_v", "16"),
                                                                    ("power($in_int_v, 3)", 0, "in_int_v", "20"),
                                                                    ("currentDate()", 3, "in_date_v", "33"),
                                                                    ("dayOfYear($in_date_v)", 3, "in_date_v", "38"),
                                                                    ("dayOfMonth($in_date_v)", 3, "in_date_v", "39"),
                                                                    ("year($in_date_v)", 3, "in_date_v", "34"),
                                                                    ("quarter($in_date_v)", 3, "in_date_v", "35"),
                                                                    ("month($in_date_v)", 3, "in_date_v", "36"),
                                                                    ("week($in_date_v)", 3, "in_date_v", "37"),
                                                                    ])
    @allure.title(
        "В качестве аргумента переменной - функции подать значение другой переменной узла"
    )
    @allure.issue("DEV-12908")
    @pytest.mark.smoke
    def test_node_calc_values_func_prim(self, super_user, diagram_all_prim_v_one_node_indirect,
                                        func, type_id, param_name, func_id):
        check_func_with_prim_value = False
        with allure.step("Создание диаграммы с узлами для обновления"):
            node_calc_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            diagram_id = diagram_all_prim_v_one_node_indirect["diagram_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        node_calc_vars1 = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name="new_func",
            type_id=type_id,
            calc_val=func,
            calc_type_id="2",
            func_ids=[func_id]
        )
        node_calc_upd1 = node_update_construct(
            700,
            202.22915649414062,
            "var_calc",
            temp_version_id,
            [node_calc_vars1],
        )
        update_node(super_user, node_id=node_calc_id, body=node_calc_upd1)

        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_calc_id).body
        )
        for prop in node_view.properties["calculate"]:
            if prop["expression"]["calculateExpressionValue"] == func:
                check_func_with_prim_value = True
                break
        assert (
                node_view.validFlag
                and check_func_with_prim_value
        )

    @allure.story(
        "В качестве значения атрибута можно выставить многократно вложенный в комплекс тип примитив "
        "$compl_type.compl_attr.primitive_attr "
    )
    @allure.title(
        "В качестве значения атрибута узла подать примитив, вложенный в комплекс тип, вложенный в комплекс тип из "
        "входной в узел переменной"
    )
    @pytest.mark.scenario("DEV-15456")
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_with_cmplx_attr",
                                               varType="in", isComplex=True, isArray=False,
                                               isConst=False, varValue="complex_type_complex_attr"),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_included_types_in_included_types(
            self,
            super_user,
            diagram_constructor,
    ):
        # create_diagram_compl_var_with_compl_attr_with_int_start_finish_calc_nodes_linked
        template: DiagramViewDto = diagram_constructor["diagram_info"]
        param: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx_with_cmplx_attr"]
        complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
        complex_type_include: ComplexTypeGetFullView = diagram_constructor["inner_complex_type"]
        node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        node_calc_id = node_calc.nodeId
        param_name = param.parameterName
        include_type_name = complex_type.attributes[0]["attributeName"]
        attr_name = complex_type_include.attributes[0]["attributeName"]

        var_name = "node_attribute"
        node_calc_vars = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name=var_name,
            type_id="1",
            calc_val=f"${param_name}.{include_type_name}.{attr_name}",
            calc_type_id="1")
        node_calc_upd = node_update_construct(
            700, 202.22915649414062, "var_calc", template.versionId, [node_calc_vars])
        update_node(super_user, node_id=node_calc_id, body=node_calc_upd)
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_calc_id).body
        )

        assert (
                node_view.validFlag
                and node_view.availableToMap[0]["variableName"]
                in node_view.properties["calculate"][0]["expression"][
                    "calculateExpressionValue"
                ]
                and node_view.availableToMap[0]["isComplex"]
                and node_view.availableToMap[0]["typeId"] == complex_type.versionId
        )

    @allure.story(
        "Все переменные расчитанные в узле или присутствуюшие в availableToMap  появляются в списке availableToMap  "
        "следующего блока. "
    )
    @allure.title(
        "Атрибуты, созданные в узле рассчёта и переданные в него предыдущим узлом отображаются в списке "
        "входных переменных следующего связанного с ним узла"
    )
    @pytest.mark.scenario("DEV-15456")
    @allure.issue("DEV-9588")
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.smoke
    def test_node_calc_vars_appear_in_inp_vars_of_next_node(
            self, super_user, diagram_constructor
    ):
        temp_version_id = diagram_constructor["temp_version_id"]
        node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
        node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
        node_calc_attr = variables_for_node(node_type="var_calc",
                                            is_arr=False,
                                            is_compl=False,
                                            name="node_attribute",
                                            type_id="1",
                                            vers_id=None,
                                            calc_val="3",
                                            calc_type_id="1")
        node_calc_upd = node_update_construct(700, 202.22915649414062, "var_calc", temp_version_id,
                                              [node_calc_attr])
        update_node(super_user, node_id=node_calc.nodeId, body=node_calc_upd)

        node_end_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_end.nodeId).body
        )
        assert (
                any(
                    inp_var["variableName"] == node_calc_attr.variableName
                    for inp_var in node_end_view.availableToMap
                )
                and len(node_end_view.availableToMap) == 2
        )
