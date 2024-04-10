import uuid

import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import DiagramInOutParameterFullViewDto, ResponseDto, ComplexTypeGetFullView, \
    NodeViewWithVariablesDto
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_diagram import update_diagram_parameters, get_diagram_parameters
from products.Decision.framework.steps.decision_steps_nodes import get_node_by_id
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.custom_type_constructors import attribute_construct
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct
from products.Decision.utilities.variable_constructors import variable_construct


@allure.epic("Диаграммы")
@allure.feature("Обновление диаграммы")
class TestDiagramsUpdate:
    @allure.story("Добавляются переменные и массивы простого типа, complexFlag = false")
    @allure.title("Добавить non-complex, non array/array переменную в параметры, проверить, что изменились")
    @pytest.mark.scenario("DEV-15441")
    @pytest.mark.parametrize('array_flag,order_num', [(False, 0),
                                                      (True, 1)])
    @pytest.mark.parametrize('type_id', [0, 1, 2, 3, 4, 5, 6, 7])
    @pytest.mark.smoke
    def test_update_diagram_parameters_non_complex_non_array(self, super_user, create_temp_diagram,
                                                             type_id, array_flag, order_num):
        complex_param_found = True
        array_param_found = False
        type_id_correct = False
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание данных параметров"):
            rand_string_param_name = generate_diagram_name_description(8, 1)["rand_name"]
            parameter_version_id2 = str(uuid.uuid4())
        with allure.step("Обновить параметры"):
            params_response = update_diagram_parameters(super_user,
                                                        temp_version_id,
                                                        [variable_construct(),
                                                         variable_construct(array_flag=array_flag,
                                                                            complex_flag=False,
                                                                            default_value=None,
                                                                            is_execute_status=None,
                                                                            order_num=order_num,
                                                                            param_name=rand_string_param_name,
                                                                            parameter_type="in_out",
                                                                            parameter_version_id=parameter_version_id2,
                                                                            parameter_id=parameter_version_id2,
                                                                            type_id=type_id
                                                                            )])
            update_response: ResponseDto = params_response.body
        with allure.step("Поиск диаграммы по айди версии"):
            parameters = get_diagram_parameters(super_user, temp_version_id).body
        with allure.step(
                "Проверка, что arrayFlag соответствует ожидаемому и что параметр не комплексный"):
            for param in parameters["inOutParameters"]:
                if param["parameterName"] == rand_string_param_name:
                    if param["complexFlag"]:
                        complex_param_found = True
                    else:
                        complex_param_found = False
                    if param["arrayFlag"]:
                        array_param_found = True
                    else:
                        array_param_found = False
                    if param["typeId"] == str(type_id):
                        type_id_correct = True
            assert len(parameters["inOutParameters"]) == 2 and not complex_param_found \
                   and array_param_found == array_flag and type_id_correct

    @allure.story("Добавляются переменные и массивы комплексного типа, complexFlag = true")
    @allure.title("Добавить комплексную переменную в параметры, проверить, что изменились")
    @pytest.mark.scenario("DEV-15441")
    @pytest.mark.parametrize('array_flag,complex_flag', [(False, True),
                                                         (True, True)])
    @pytest.mark.smoke
    def test_update_diagram_parameters_complex_array(self, super_user,
                                                     create_custom_types_gen,
                                                     create_temp_diagram,
                                                     array_flag, complex_flag):
        complex_param_found = False
        type_name = "ag_ctype_" + generate_string()
        create_result: ResponseDto = create_custom_types_gen.create_type(
            type_name, [attribute_construct()]
        )
        custom_type_version_id = create_result.uuid
        with allure.step("Поиск созданного типа"):
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        type_id = complex_type.versionId
        rand_string_param_name = generate_diagram_name_description(8, 1)["rand_name"]
        parameter_version_id = str(uuid.uuid4())
        with allure.step("Обновить параметры, добавив комплексный тип"):
            params_response = update_diagram_parameters(super_user,
                                                        temp_version_id,
                                                        [variable_construct(),
                                                         variable_construct(array_flag=array_flag,
                                                                            complex_flag=complex_flag,
                                                                            default_value=None,
                                                                            is_execute_status=None,
                                                                            order_num=0,
                                                                            param_name=rand_string_param_name,
                                                                            parameter_type="in_out",
                                                                            parameter_version_id=parameter_version_id,
                                                                            parameter_id=parameter_version_id,
                                                                            type_id=type_id,
                                                                            )])
            update_response: ResponseDto = params_response.body
        with allure.step("Поиск диаграммы по айди версии и проверка, что комплексный параметр появился"):
            parameters = get_diagram_parameters(super_user, temp_version_id).body
            for param in parameters["inOutParameters"]:
                if param["complexFlag"]:
                    complex_param_found = True
            assert len(parameters["inOutParameters"]) == 2 and complex_param_found

    @allure.story("Добавляются переменные, выбранные из списка справочников, соответствующего типа")
    @allure.title("Добавить переменную, связанную со справочниками в параметры, проверить, что изменились")
    @pytest.mark.scenario("DEV-15441")
    @pytest.mark.parametrize('array_flag,dict_flag', [(False, True),
                                                      (True, True)])
    @pytest.mark.smoke
    def test_update_diagram_parameters_dict_array(self, super_user, create_dict_gen,
                                                  create_temp_diagram,
                                                  array_flag, dict_flag):
        dict_param_found = False
        with allure.step("Создание справочника для переменной диаграммы"):
            dict_name = "ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"]
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="age")
            custom_attr = dict_construct(
                dict_name=dict_name,
                dict_value_type_id="1",
                values=[value])
            dict_create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Задание параметров переменной"):
            rand_string_param_name = generate_diagram_name_description(8, 1)["rand_name"]
            parameter_version_id = str(uuid.uuid4())
            diagram_param = variable_construct(array_flag=False,
                                               complex_flag=False,
                                               default_value=None,
                                               is_execute_status=None,
                                               order_num=0,
                                               param_name=rand_string_param_name,
                                               parameter_type="in_out",
                                               parameter_version_id=parameter_version_id,
                                               parameter_id=parameter_version_id,
                                               type_id=1,
                                               dict_flag=True,
                                               dict_id=dict_create_result.uuid,
                                               dict_name=dict_name
                                               )
        with allure.step("Обновить параметры, добавив комплексный тип"):
            params_response = update_diagram_parameters(super_user,
                                                        temp_version_id,
                                                        [variable_construct(),
                                                         diagram_param])
            update_response: ResponseDto = params_response.body
        with allure.step("Поиск диаграммы по айди версии и проверка, что комплексный параметр появился"):
            parameters = get_diagram_parameters(super_user, temp_version_id).body
            for param in parameters["inOutParameters"]:
                if param["dictFlag"] and \
                        param["dictId"] == dict_create_result.uuid and \
                        param["dictName"] == dict_name:
                    dict_param_found = True
            assert len(parameters["inOutParameters"]) == 2 and dict_param_found

    @allure.story("Имя каждой переменной должно быть уникально")
    @allure.title("Добавить второй параметр с именем, дублирующим первый")
    @pytest.mark.scenario("DEV-15441")
    @allure.issue("DEV-4086")
    def test_update_diagram_parameters_unique(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание данных параметров"):
            rand_string_param_name = generate_diagram_name_description(8, 1)["rand_name"]
            parameter_version_id1 = str(uuid.uuid4())
            parameter_version_id2 = str(uuid.uuid4())
        with allure.step("Задание первого параметра"):
            update_diagram_parameters(super_user,
                                      temp_version_id,
                                      [variable_construct(),
                                       variable_construct(array_flag=False,
                                                          complex_flag=False,
                                                          default_value=None,
                                                          is_execute_status=None,
                                                          order_num=0,
                                                          param_name=rand_string_param_name,
                                                          parameter_type="in_out",
                                                          parameter_version_id=parameter_version_id2,
                                                          type_id=1
                                                          )])
        with allure.step("Задание второго параметра с именем, дублирующим первый запрещено"):
            with pytest.raises(HTTPError):
                assert update_diagram_parameters(super_user,
                                                 temp_version_id,
                                                 [variable_construct(),
                                                  variable_construct(array_flag=False,
                                                                     complex_flag=False,
                                                                     default_value=None,
                                                                     is_execute_status=None,
                                                                     order_num=0,
                                                                     param_name=rand_string_param_name,
                                                                     parameter_type="in_out",
                                                                     parameter_version_id=parameter_version_id1,
                                                                     type_id=1
                                                                     ),
                                                  variable_construct(array_flag=False,
                                                                     complex_flag=False,
                                                                     default_value=None,
                                                                     is_execute_status=None,
                                                                     order_num=1,
                                                                     param_name=rand_string_param_name,
                                                                     parameter_type="in_out",
                                                                     parameter_version_id=parameter_version_id2,
                                                                     type_id=1
                                                                     )]).status == 400

    @allure.story("Имя переменной должно начинаться с буквы латинского алфавита")
    @allure.title("Создать параметр, имя которого начинается с невалидного начального символа")
    @pytest.mark.scenario("DEV-15441")
    @pytest.mark.parametrize('bad_symbol', ["!", "1", "ь"])
    def test_update_diagram_parameters_bad_start_symbol(self, super_user,
                                                        create_temp_diagram, bad_symbol):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание данных параметров"):
            rand_string_param_name = generate_diagram_name_description(8, 1)["rand_name"]
            parameter_version_id2 = str(uuid.uuid4())
        with allure.step("Задание первого параметра с именем, начинающимся с цифры"):
            with pytest.raises(HTTPError):
                assert update_diagram_parameters(super_user,
                                                 temp_version_id,
                                                 [variable_construct(),
                                                  variable_construct(array_flag=False,
                                                                     complex_flag=False,
                                                                     default_value=None,
                                                                     is_execute_status=None,
                                                                     order_num=0,
                                                                     param_name=bad_symbol + rand_string_param_name,
                                                                     parameter_type="in_out",
                                                                     parameter_version_id=parameter_version_id2,
                                                                     type_id=1
                                                                     )]).status == 400

    @allure.story("Имя переменной не должно превышать 40 символов")
    @allure.title("Создать параметр, имя которого начинается допустимой длины")
    @pytest.mark.scenario("DEV-15441")
    @pytest.mark.parametrize('name_length, status', [(39, 200), (40, 200)])
    def test_update_diagram_parameters_name_lenght(self, super_user,
                                                   create_temp_diagram,
                                                   name_length, status):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание данных параметров"):
            rand_string_param_name = generate_diagram_name_description(name_length, 1)["rand_name"]
            parameter_version_id2 = str(uuid.uuid4())
        with allure.step("Задание первого параметра с именем заданной длины"):
            params_response = update_diagram_parameters(super_user,
                                                        temp_version_id,
                                                        [variable_construct(),
                                                         variable_construct(array_flag=False,
                                                                            complex_flag=False,
                                                                            default_value=None,
                                                                            is_execute_status=None,
                                                                            order_num=0,
                                                                            param_name=rand_string_param_name,
                                                                            parameter_type="in_out",
                                                                            parameter_version_id=parameter_version_id2,
                                                                            type_id=1
                                                                            )])
        with allure.step("Проверка, что клиенту запрещено создать параметр, имя которого превышает "
                         "допустимую длину"):
            assert params_response.status == status

    @allure.story("Имя переменной не должно превышать 25 символов")
    @allure.title("Создать параметр, имя которого больше 40 символов по длине")
    @pytest.mark.scenario("DEV-15441")
    @pytest.mark.parametrize('name_length, status', [(41, 400)])
    def test_update_diagram_parameters_name_lenght_neg(self, super_user,
                                                       create_temp_diagram,
                                                       name_length, status):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Создание данных параметров"):
            rand_string_param_name = generate_diagram_name_description(name_length, 1)["rand_name"]
            parameter_version_id2 = str(uuid.uuid4())
        with allure.step("Задание параметра с именем больше 25 символов запрещено"):
            with pytest.raises(HTTPError):
                assert update_diagram_parameters(super_user,
                                                 temp_version_id,
                                                 [variable_construct(),
                                                  variable_construct(array_flag=False,
                                                                     complex_flag=False,
                                                                     default_value=None,
                                                                     is_execute_status=None,
                                                                     order_num=0,
                                                                     param_name=rand_string_param_name,
                                                                     parameter_type="in_out",
                                                                     parameter_version_id=parameter_version_id2,
                                                                     type_id=1
                                                                     )]).status == status

    @allure.story("diagram execute status переменная диаграммы должна передаваться из запроса создания шаблона "
                  "диаграммы при обновлении параметров диаграммы.")
    @allure.title("Задать новую переменную, взяв diagram execute status из созданного шаблона, проверить, что успешно")
    @pytest.mark.scenario("DEV-15441")
    @allure.issue("DEV-7187")
    def test_add_parameter_with_exec_from_template(self, super_user,
                                                   create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
            diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
                **diagram_template["inOutParameters"][0])
        with allure.step("Создание данных параметров"):
            param_name = "in_out_var"
            parameter_version_id2 = str(uuid.uuid4())
        with allure.step("Задание первого параметра с именем заданной длины"):
            params_response = update_diagram_parameters(super_user,
                                                        temp_version_id,
                                                        [diagram_exec_var,
                                                         variable_construct(array_flag=False,
                                                                            complex_flag=False,
                                                                            default_value=None,
                                                                            is_execute_status=None,
                                                                            order_num=0,
                                                                            param_name=param_name,
                                                                            parameter_type="in_out",
                                                                            parameter_version_id=parameter_version_id2,
                                                                            type_id=1
                                                                            )])
        with allure.step("Проверка, что клиенту запрещено создать параметр, имя которого превышает "
                         "допустимую длину"):
            assert params_response.status == 200

    @allure.story("Все входные и выходные переменные диаграммы доступны в центральном узле")
    @allure.title("Создать диаграмму с параметрами всех типов, проверить, что переменные доступны")
    @pytest.mark.scenario("DEV-15440")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variable_availability(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
        with allure.step("Получение центрального узла диаграммы"):
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что количество переменных пришедших в центральный узел с обеих сторон совпадает с "
                         "количеством переменных диаграммы"):
            assert len(param_check_node_view.availableToMap) == len(all_in_params) \
                   and len(param_check_node_view.availableToCalc) == len(all_out_params) + len(all_in_params)

    @allure.story("После удаления входных переменных они недоступны в центральном узле")
    @allure.title("Создать диаграмму с параметрами всех типов, удалить входные переменные, проверить, что удаленные "
                  "переменные недоступны")
    @pytest.mark.scenario("DEV-15440")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_in_deleted_unavailable(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Формирование обновленного состава переменных диаграммы"):
            new_all_params = all_out_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
        with allure.step("Получение центрального узла диаграммы"):
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка, что входные переменные не пришли в узел"):
            assert param_check_node_view.availableToMap is None

    @allure.story("После удаления выходных переменных они недоступны в центральном узле")
    @allure.title("Создать диаграмму с параметрами всех типов, удалить выходные переменные, проверить, что удаленные "
                  "переменные недоступны")
    @pytest.mark.scenario("DEV-15440")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_out_deleted_unavailable(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Формирование обновленного состава переменных диаграммы"):
            new_all_params = all_in_params + diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
        with allure.step("Получение центрального узла диаграммы"):
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка, что выходные переменные не пришли в узел"):
            assert len(param_check_node_view.availableToCalc) == len(all_in_params)

    @allure.story("При изменении флага массива в переменной на вход, флаг меняется в центральном узле")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг на переменных на вход")
    @pytest.mark.scenario("DEV-15440")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False},
                                                                      {"node": "var_calc", "array_flag": True}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_update_in_var_arr_flag(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            flag_on_the_start = diagram_all_prim_v_one_node_indirect["array_flag"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Смена флагов и обновление переменных диаграммы"):
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
            for input_variable in param_check_node_view.availableToMap:
                assert input_variable["isArray"] is not flag_on_the_start

    @allure.story("При изменении флага массива в переменной на выход, флаг меняется в центральном узле")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг на переменных на вход, "
                  "проверить что сменился в центральном узле")
    @pytest.mark.scenario("DEV-15440")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_update_out_var_arr_flag(self, super_user, diagram_all_prim_v_one_node_indirect):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            flag_on_the_start = all_out_params[0].arrayFlag
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Смена флагов переменных и обновление переменных"):
            for variable in all_out_params:
                variable.arrayFlag = not variable.arrayFlag
            new_all_params = all_in_params + \
                             all_out_params + \
                             diagram_exec_var
            params_response = update_diagram_parameters(super_user,
                                                        diagram_all_prim_v_one_node_indirect["temp_version_id"],
                                                        new_all_params)
            param_check_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, param_check_node_id).body
            )
        with allure.step("Проверка что все переменные центрального узла изменили флаг"):
            for output_variable in param_check_node_view.availableToCalc:
                if output_variable["variableName"].startswith("out"):
                    assert output_variable["isArray"] is not flag_on_the_start

    @allure.story("При изменении типа входной переменной на комплексный - тип и флаг меняются в центральном узле")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг и тип на входных переменных, "
                  "проверить что сменился в центральном узле")
    @pytest.mark.scenario("DEV-15440")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_update_in_var_ctype_flag(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                create_custom_types_gen):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Создание комплексного типа"):
            ctype_name = "attr_" + generate_string()
            create_response: ResponseDto = create_custom_types_gen.create_type(ctype_name, [attribute_construct()])
            ctype_version_id = create_response.uuid
        with allure.step("Смена флагов и типов входных переменных и обновление переменных диаграммы"):
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
            for input_variable in param_check_node_view.availableToMap:
                assert input_variable["isComplex"] and input_variable["typeId"] == ctype_version_id

    @allure.story("При изменении типа выходной переменной на комплексный - тип и флаг меняются в центральном узле")
    @allure.title("Создать диаграмму с параметрами всех типов, поменять флаг и тип на выходных переменных, "
                  "проверить что сменился в центральном узле")
    @pytest.mark.scenario("DEV-15440")
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_update_out_var_ctype_flag(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                 create_custom_types_gen):
        with allure.step("Получение переменных диаграммы"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Создание комплексного типа"):
            ctype_name = "attr_" + generate_string()
            create_response: ResponseDto = create_custom_types_gen.create_type(ctype_name, [attribute_construct()])
            ctype_version_id = create_response.uuid
        with allure.step("Смена флагов и типов выходных переменных и обновление переменных диаграммы"):
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
            for output_variable in param_check_node_view.availableToCalc:
                if output_variable["variableName"].startswith("out"):
                    assert output_variable["isComplex"] and output_variable["typeId"] == ctype_version_id

    @allure.story("При изменении типа выходной переменной на справочник - флаг и dictId появляются в центральном узле")
    @allure.title(
        "Создать диаграмму с параметрами всех типов, поменять флаг и добавтить dictId на выходных переменных, "
        "проверить что сменился в центральном узле")
    @pytest.mark.scenario("DEV-15440")
    @allure.issue("DEV-13548")
    @pytest.mark.dict_types(["all_types"])
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_update_in_var_dict_flag(self, super_user, diagram_all_prim_v_one_node_indirect,
                                               create_custom_custom_attributes):
        with allure.step("Получение переменных диаграммы и идентификаторов справочников"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
            all_in_params = diagram_all_prim_v_one_node_indirect["all_in_params"]
            all_out_params = diagram_all_prim_v_one_node_indirect["all_out_params"]
            diagram_exec_var = [diagram_all_prim_v_one_node_indirect["diagram_exec_var"]]
        with allure.step("Смена флагов и типов выходных переменных и обновление переменных диаграммы"):
            dicts = create_custom_custom_attributes
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
            for input_variable in param_check_node_view.availableToMap:
                assert input_variable["isDict"] and input_variable.get("dictId") == dicts[input_variable["typeId"]].id

    @allure.story("При изменении типа выходной переменной на справочник - флаг и dictId меняются в центральном узле")
    @allure.title(
        "Создать диаграмму с параметрами всех типов, поменять флаг и добавтить dictId на выходных переменных, "
        "проверить что сменился в центральном узле")
    @pytest.mark.scenario("DEV-15440")
    @allure.issue("DEV-13548")
    @pytest.mark.dict_types(["all_types"])
    @pytest.mark.parametrize("diagram_all_prim_v_one_node_indirect", [{"node": "var_calc", "array_flag": False}],
                             indirect=["diagram_all_prim_v_one_node_indirect"])
    @pytest.mark.smoke
    def test_variables_update_out_var_dict_flag(self, super_user, diagram_all_prim_v_one_node_indirect,
                                                create_custom_custom_attributes):
        with allure.step("Получение переменных диаграммы и идентификаторов справочников"):
            param_check_node_id = diagram_all_prim_v_one_node_indirect["testing_node_id"]
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
        with allure.step("Проверка что все переменные центрального узла изменили флаг и получили верный "
                         "идентификатор словаря"):
            for output_variable in param_check_node_view.availableToCalc:
                if output_variable["variableName"].startswith("out"):
                    assert output_variable["isDict"]
                    assert output_variable.get("dictId") == dicts[output_variable["typeId"]].id
