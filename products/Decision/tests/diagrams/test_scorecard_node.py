import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, DiagramViewDto, NodeViewShortInfo, \
    DiagramInOutParameterFullViewDto, \
    NodeViewWithVariablesDto, NodeValidateDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version, validate_diagram
from products.Decision.framework.steps.decision_steps_diagram_helpers import upload_scorecard_file
from products.Decision.framework.steps.decision_steps_nodes import create_node, delete_node_by_id, get_node_by_id, \
    update_node, validate_node
from products.Decision.utilities.custom_models import IntValueType, VariableParams
from products.Decision.utilities.node_cunstructors import scorecard_node_construct, scorecard_output_var, \
    score_val_construct, scorecard_input_var, scorecard_properties


@allure.epic("Диаграммы")
@allure.feature("Узел скоркарты")
class TestScorecardNode:
    @allure.story("Узел скоркарты создаётся")
    @allure.title(
        "Создать диаграмму с узлом скоркарты без параметров, проверить что создался"
    )
    @pytest.mark.scenario("DEV-15457")
    @pytest.mark.smoke
    def test_create_scorecard_node(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
        with allure.step("Создание узла скоркарты"):
            node_scorecard = scorecard_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_scorecard_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_scorecard).body
            )
            node_scorecard_id = node_scorecard_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла скоркарты корректен и равен 9-расчет скоркарты"
        ):
            assert diagram.nodes[str(node_scorecard_id)].nodeTypeId == 9

    @allure.story("Узел скоркарты можно удалить")
    @allure.title("Удалить узел скоркарты без параметров")
    @pytest.mark.scenario("DEV-15457")
    @pytest.mark.smoke
    def test_delete_node_scorecard(self, super_user, create_temp_diagram):
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
        with allure.step("Создание узла скоркарты"):
            node_scorecard = scorecard_node_construct(
                700, 202.22915649414062, template["versionId"], None
            )
            node_scorecard_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_scorecard).body
            )
            node_scorecard_id = node_scorecard_response.uuid
        with allure.step("Удаление узла скоркарты по id"):
            delete_node_by_id(super_user, node_scorecard_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert get_node_by_id(super_user, node_scorecard_id)

    @allure.story("Нет ошибок, если узел корректно заполнен")
    @allure.title("Cоздание диаграммы с заполненным узлом скоркарты")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_create_diagram_with_node_scorecard(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            node_end_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=1,
                                            max_value=10,
                                            include_min_val=False,
                                            include_max_val=True,
                                            value=None,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )
            get_node_by_id(super_user, node_end_id)
        with allure.step("Проверка, что узел валиден"):
            assert node_view.validFlag

    @allure.story("Предусмотрена проверка на то, что Значение скорбалла по умолчанию и Скорбалл >=<0 и дробный")
    @allure.title("Создание диаграммы с заполненным узлом скоркарты и значением скорбала по умолчанию 0, 1, 0.2")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.parametrize("default_value", [1.2, 1, 0, -1])
    @pytest.mark.smoke
    def test_create_diagram_with_node_scorecard_default_value(self, super_user, default_value,
                                                              diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=default_value,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=None,
                                            max_value=None,
                                            include_min_val=None,
                                            include_max_val=None,
                                            value=20,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=default_value, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация прошла успешно"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )

        assert node_view.validFlag

    @allure.story("Предусмотрена проверка на то, что в маппинге значение соответствует типу переменной")
    @allure.title("Создание диаграммы с заполненным узлом скоркарты и значением строковым")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_create_diagram_with_node_scorecard_value_map_negative(self, super_user,
                                                                   diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=None,
                                            max_value=None,
                                            include_min_val=None,
                                            include_max_val=None,
                                            value="строка",
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация не прошла, получаем описание ошибки"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )

        assert not node_view.validFlag and \
               node_view.validationPayload["nodeValidationMap"]["scoreValues"][score_val.rowKey]["value"] \
               == "Тип значения, не соответствует типу входного параметра"

    @allure.story("Предусмотрена проверка на то, что выбран выходной параметр - фронт")
    @allure.title("Создание диаграммы с  заполненным узлом скоркарты и без выходного параметра")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @allure.issue("DEV-12974")
    def test_create_diagram_with_node_scorecard_without_output_var(self, super_user,
                                                                   diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_val = score_val_construct(min_value=5,
                                            max_value=10,
                                            include_min_val=False,
                                            include_max_val=True,
                                            value=None,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)

            score_properties = scorecard_properties(output_variable=None,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация не прошла"):
            with pytest.raises(HTTPError, match="422"):
                assert validate_diagram(super_user, temp_version_id).body["message"] \
                       == "На узле - Расчет скоркарты, есть ошибки."

    @allure.story("Предусмотрена проверка на наличие хотя бы одного входного параметра - фронт")
    @allure.title("Создание диаграммы с  заполненным узлом скоркарты и без входного параметра")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @allure.issue("DEV-12974")
    def test_create_diagram_with_node_scorecard_without_input_var(self, super_user,
                                                                  diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id="1")

            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация не прошла"):
            with pytest.raises(HTTPError, match="422"):
                assert validate_diagram(super_user, temp_version_id).body["message"] \
                       == "На узле - Расчет скоркарты, есть ошибки."

    @allure.story("Предусмотрена проверка на то, что для нечисловых параметров в маппинге "
                  "отсутствует повторение значений в поле “Значение”")
    @allure.title("Создание диаграммы с заполненным узлом скоркарты с входной переменной строкового"
                  " типа и повторяющимся значением в поле значение")
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-9692")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.parametrize("param_name, repeat_val, type_id",
                             [("in_str_param", "some_string", IntValueType.str),
                              ("in_bool_param", "true", IntValueType.bool),
                              ("in_date_param", "2023-04-23", IntValueType.date),
                              ("in_date_time_param", "2023-04-24 17:06:13.000", IntValueType.dateTime),
                              ("in_time_param", "09:00:00", IntValueType.time)],
                             ids=["string", "boolean", "date", "date_time", "time"])
    @pytest.mark.smoke
    def test_create_diagram_node_scorecard_not_num_var(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                       param_name, repeat_val, type_id):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            node_end_id = diagram_all_prim_v_one_node_indirect["node_end_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect[param_name]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=None,
                                            max_value=None,
                                            include_min_val=None,
                                            include_max_val=None,
                                            value=repeat_val,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=type_id,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            input_score_var2 = scorecard_input_var(is_arr=False, is_compl=False,
                                                   default_value=1, is_dict=False,
                                                   name=score_param.parameterName, type_id=type_id,
                                                   score_values=[score_val],
                                                   param_id=score_param.parameterId)

            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var, input_score_var2])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_end_id).body
            )

        with allure.step("Проверка что валидация не прошла"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )

            assert not node_view.validFlag and \
                   node_view.validationPayload["nodeValidationMap"]["scoreValues"][score_val.rowKey]["value"] \
                   == "Диапазоны значений параметра скоркарты не должны пересекаться"

    @allure.story("Предусмотрена проверка на то, что выходной параметр - переменная целого типа"
                  " (INT или LONG, дробный)")
    @allure.title("Создание диаграммы с  заполненным узлом скоркарты с вsходной переменной типа"
                  " (INT или LONG, дробный)")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.parametrize("type_id", [0, 1, 7])
    @pytest.mark.smoke
    def test_create_diagram_node_scorecard_out_var_int_long(self, super_user, type_id,
                                                            diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id=type_id)
            score_val = score_val_construct(min_value=None,
                                            max_value=None,
                                            include_min_val=None,
                                            include_max_val=None,
                                            value=5,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация прошла успешно"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )

            assert node_view.validFlag

    @allure.story("Предусмотрена проверка на то, что выходной параметр - переменная целого типа"
                  " (INT или LONG, дробный)")
    @allure.title("Создание диаграммы с  заполненным узлом скоркарты с выходной переменной типа INT"
                  " и заменой на другой тип (LONG, дробный) при обновлении")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("type_id", [IntValueType.str, IntValueType.date, IntValueType.dateTime,
                                         IntValueType.time, IntValueType.bool],
                             ids=["str", "date", "date_time", "time", "boolean"])
    # @allure.issue(url="DEV-9753")
    def test_create_diagram_node_scorecard_out_var_put(self, super_user, type_id, diagram_scorecard):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_scorecard["node_score_id"]
            temp_version_id = diagram_scorecard["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_scorecard["score_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            wrong_output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                          is_dict=False, default_value=1,
                                                          name=score_var_name, type_id=type_id)
            score_val = score_val_construct(min_value=1,
                                            max_value=10,
                                            include_min_val=False,
                                            include_max_val=True,
                                            value=None,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=wrong_output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )
        with allure.step("Проверка что валидация не прошла"):
            with pytest.raises(HTTPError, match="422"):
                assert validate_diagram(super_user, temp_version_id).body["message"] \
                       == "На узле - Расчет скоркарты, есть ошибки."

    @allure.story("Предусмотрена проверка на то, что для каждого из входных "
                  "параметров указано значение по умолчанию (defaultScore)")
    @allure.title("Создание диаграммы с заполненным узлом скоркарты и где у входной переменной "
                  "не указано значение по умолчанию (defaultScore)")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_create_diagram_with_node_scorecard_without_defaultvalue_in(self, super_user,
                                                                        diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=None,
                                            max_value=None,
                                            include_min_val=None,
                                            include_max_val=None,
                                            value=5,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=None, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация не прошла, получаем описание ошибки"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )

            assert not node_view.validFlag and \
                   node_view.validationPayload["nodeValidationMap"]["inputVariablesMapping"][input_score_var.rowKey][
                       "defaultValue"] \
                   == "Поле обязательно для заполнения"

    @allure.story("Предусмотрена проверка на то, что указаны параметры outputVariable"
                  " (variable, variableTypeID, defaultValue)")
    @allure.title("Создание диаграммы с заполненным узлом скоркарты и где у выходной переменной "
                  "не указано значение по умолчанию (defaultScore)")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_create_diagram_with_node_scorecard_without_defaultvalue_out(self, super_user,
                                                                         diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=None,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=None,
                                            max_value=None,
                                            include_min_val=None,
                                            include_max_val=None,
                                            value=5,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация не прошла, получаем описание ошибки"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )

            assert not node_view.validFlag and \
                   node_view.validationPayload["nodeValidationMap"]["outputVariable"][output_score_var.rowKey][
                       "defaultValue"] \
                   == "Поле обязательно для заполнения"

    @allure.story("Предусмотрена проверка на то, что для числовых параметров/дат/даты_времени/времени "
                  "в маппинге отсутствует пересечение указанных диапазонов")
    @allure.title("Создание диаграммы с  заполненным узлом скоркарты и пересечением диапазонов "
                  "значений для даты, date_time, времени")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.parametrize("param_name, interval_vals, type_id", [("in_date_param",
                                                                     ("2023-04-23", "2023-04-24",
                                                                      "2023-04-24", "2023-04-25"),
                                                                     3),
                                                                    ("in_date_time_param",
                                                                     ("2023-04-24 17:06:13.000",
                                                                      "2023-04-25 17:06:13.000",
                                                                      "2023-04-25 17:06:13.000",
                                                                      "2023-04-26 17:06:13.000"),
                                                                     5),
                                                                    ("in_time_param",
                                                                     ("09:00:00", "10:00:00",
                                                                      "10:00:00", "11:00:00"),
                                                                     6),
                                                                    ("in_int_param",
                                                                     (5, 10,
                                                                      10, 15),
                                                                     1),
                                                                    ("in_long_param",
                                                                     (5, 10,
                                                                      10, 15),
                                                                     7)
                                                                    ])
    def test_create_diagram_with_node_scorecard_wrong_interval(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                               param_name, interval_vals, type_id):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect[param_name]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=interval_vals[0],
                                            max_value=interval_vals[1],
                                            include_min_val=False,
                                            include_max_val=True,
                                            value=None,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=type_id,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_val2 = score_val_construct(min_value=interval_vals[2],
                                             max_value=interval_vals[3],
                                             include_min_val=True,
                                             include_max_val=True,
                                             value=None,
                                             score_value=15)
            input_score_var2 = scorecard_input_var(is_arr=False, is_compl=False,
                                                   default_value=1, is_dict=False,
                                                   name=score_param.parameterName, type_id=type_id,
                                                   score_values=[score_val2],
                                                   param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var, input_score_var2])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=node_score_id, body=node_score_upd
            )

        with allure.step("Проверка что валидация  не прошла, описание ошибки"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_score_id).body
            )

            assert not node_view.validFlag and \
                   node_view.validationPayload["nodeValidationMap"]["scoreValues"][score_val.rowKey]["value"] \
                   == "Диапазоны значений параметра скоркарты не должны пересекаться"

    @allure.story("Предусмотрена проверка на то, что заполнены nodeName и nodeType")
    @allure.title("Cоздание диаграммы с не заполненным nodeName и nodeType, обновление не происходит")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "scorecard", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    def test_create_diagram_with_node_scorecard_without_node_name_node_type(self, super_user,
                                                                            diagram_all_prim_v_one_node_indirect):
        with allure.step("Создание временной версии диаграммы с узлом скоркарты"):
            node_score_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            temp_version_id = diagram_all_prim_v_one_node_indirect["temp_version_id"]
            score_param: DiagramInOutParameterFullViewDto = diagram_all_prim_v_one_node_indirect["in_int_param"]
        with allure.step("Обновление узла скоркарты"):
            score_var_name = "new_v"
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=1,
                                                    name=score_var_name, type_id="1")
            score_val = score_val_construct(min_value=1,
                                            max_value=10,
                                            include_min_val=False,
                                            include_max_val=True,
                                            value=None,
                                            score_value=10)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=score_param.parameterName, type_id=1,
                                                  score_values=[score_val],
                                                  param_id=score_param.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            node_score_upd.nodeTypeId = None
            node_score_upd.nodeName = None
        with pytest.raises(HTTPError, match="400"):
            assert validate_node(
                super_user, node_id=node_score_id, body=NodeValidateDto.construct(
                    nodeTypeId=node_score_upd.nodeTypeId,
                    properties=node_score_upd.properties)
            )

    @allure.story("Загрузка скоррбаллов из файла в узле скоркарта")
    @allure.title("Значения маппинга скоррбаллов на переменные загружаются из эксель файла")
    @pytest.mark.variable_data(
        [VariableParams(varName="a", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="b", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["скоркарта"])
    def test_update_scorecard_mapping_from_excel_file(self, super_user, diagram_constructor):
        temp_version_id = diagram_constructor["temp_version_id"]
        input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["a"]
        output_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["b"]
        scorecard_node: NodeViewShortInfo = diagram_constructor["nodes"]["скоркарта"]
        with allure.step("Загрузка файла для получения значений скорркарты"):
            score_values = upload_scorecard_file(
                super_user, "products/Decision/resources/scorecard_test_values.xlsx")[0].scoreValues
        with allure.step("Добавление значений скорркарты из файла"):
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=input_var.parameterName,
                                                  type_id=input_var.typeId,
                                                  score_values=score_values,
                                                  param_id=input_var.parameterId)
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=2,
                                                    name=output_var.parameterName,
                                                    type_id=output_var.typeId,
                                                    param_id=output_var.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=scorecard_node.nodeId, body=node_score_upd
            )

        with allure.step("Проверка что валидация успешна, ошибок на узле при маппинге значений из файла не обнаружено"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, scorecard_node.nodeId).body
            )
            assert node_view.validFlag

    @allure.story("Валидация типов скоррбаллов")
    @allure.title("Предусмотрена валидация значений скоррбаллов на соответствие типу переменной маппинга")
    @pytest.mark.variable_data(
        [VariableParams(varName="a", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="b", varType="out", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["скоркарта"])
    def test_scorecard_mapping_from_excel_valid_type(self, super_user, diagram_constructor):
        temp_version_id = diagram_constructor["temp_version_id"]
        input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["a"]
        output_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["b"]
        scorecard_node: NodeViewShortInfo = diagram_constructor["nodes"]["скоркарта"]
        with allure.step("Загрузка файла для получения значений скорркарты"):
            score_values = upload_scorecard_file(
                super_user, "products/Decision/resources/scorecard_test_values.xlsx")[0].scoreValues
        with allure.step("Добавление значений скорркарты из файла с неверным типом данных"):
            for v in score_values:
                v.maxValue = str(float(int(v.maxValue)))
                v.minValue = str(float(int(v.minValue)))
                v.scoreValue = str(float(int(v.scoreValue)))
            print(score_values)
            input_score_var = scorecard_input_var(is_arr=False, is_compl=False,
                                                  default_value=1, is_dict=False,
                                                  name=input_var.parameterName,
                                                  type_id=input_var.typeId,
                                                  score_values=score_values,
                                                  param_id=input_var.parameterId)
            output_score_var = scorecard_output_var(is_arr=False, is_compl=False,
                                                    is_dict=False, default_value=2,
                                                    name=output_var.parameterName,
                                                    type_id=output_var.typeId,
                                                    param_id=output_var.parameterId)
            score_properties = scorecard_properties(output_variable=output_score_var,
                                                    input_variables=[input_score_var])
            node_score_upd = scorecard_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=temp_version_id,
                properties=score_properties,
                operation="update",
            )
            update_node(
                super_user, node_id=scorecard_node.nodeId, body=node_score_upd
            )

        with allure.step("Проверка что сработала валидация типа значения скоррбалла"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, scorecard_node.nodeId).body
            )
            assert not node_view.validFlag and list(node_view.validationPayload["nodeValidationMap"]["scoreValues"]
                                                    .values())[0]["value"] == \
                   "Указанное значение не соответствует типу переменной"
