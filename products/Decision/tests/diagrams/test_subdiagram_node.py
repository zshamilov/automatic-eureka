import uuid

import glamor as allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import (
    ResponseDto,
    DiagramViewDto,
    NodeViewShortInfo,
    DiagramInOutParameterFullViewDto,
    NodeViewWithVariablesDto, NodeValidateDto, ComplexTypeGetFullView, AttributeShortView, DiagramCreateNewVersion,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version, save_diagram,
)
from products.Decision.framework.steps.decision_steps_nodes import (
    create_node,
    update_node,
    get_node_by_id,
)
from products.Decision.utilities.custom_models import VariableParams
from products.Decision.utilities.node_cunstructors import (
    node_construct,
    variables_for_node,
    node_update_construct,
)


@allure.epic("Диаграммы")
@allure.feature("Узел поддиаграммы")
class TestDiagramsSubdiagramNode:
    @allure.story("Узел можно создать с NodeType = 14")
    @allure.title(
        "Создать диаграмму с узлом поддиаграммы без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15453")
    @pytest.mark.smoke
    def test_create_node_subdiagram_empty(self, super_user, create_temp_diagram):
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла поддиаграммы"):
            node_sub = node_construct(
                700, 202.22915649414062, "subdiagram", template["versionId"], None
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
            assert diagram.nodes[str(node_sub_id)].nodeTypeId == 14

    @allure.story("Созданный узел можно прочесть")
    @allure.title("Проверить, что возвращается корректная информация об узле")
    @pytest.mark.scenario("DEV-15453")
    @pytest.mark.smoke
    def test_read_node_subdiagram(self, super_user, create_temp_diagram):
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла поддиаграммы"):
            node_sub = node_construct(
                700, 202.22915649414062, "subdiagram", template["versionId"], None
            )
            node_sub_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_sub).body
            )
            node_sub_id = node_sub_response.uuid
        with allure.step("Получение информации об узле поддиаграммы"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        with allure.step("Проверка, что создался нужный узел"):
            assert (
                    node_view.nodeTypeId == 14
                    and node_view.nodeId == node_sub_id
                    and node_view.nodeName == "Поддиаграмма"
                    and node_view.metaInfo is not None
            )

    @allure.story("В узел можно добавить диаграмму из списка сохранённых диаграмм")
    @allure.title(
        "Создать диаграмму с узлом поддиаграммы с поддиаграммой, увидеть, что диаграмма добавилась"
    )
    @pytest.mark.scenario("DEV-15453")
    @pytest.mark.smoke
    def test_create_node_subdiagram_with_subdiag(
            self,
            super_user,
            simple_diagram,
            create_temp_start_finish_sub_int_var_linked,
    ):
        with allure.step("Создание поддиаграммы с целочисленной переменной"):
            subdiagram_version_id = simple_diagram["create_result"]["uuid"]
            subdiagram_id = simple_diagram["template"]["diagramId"]
            subdiagram_var: DiagramInOutParameterFullViewDto = (simple_diagram["diagram_param"])
            subdiagram_exec_var: DiagramInOutParameterFullViewDto = (simple_diagram["inner_diagram_execute_var"])
        with allure.step("Создание диаграммы с узлом поддиаграммы"):
            diagram_template: DiagramViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_template"]
            )
            node_sub_id = create_temp_start_finish_sub_int_var_linked["node_sub_id"]
            diagram_var: DiagramInOutParameterFullViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_variable"]
            )
            inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False,
                                                  name="diagram_execute_status", type_id="2",
                                                  node_variable="diagram_execute_status",
                                                  outer_variable_id=subdiagram_exec_var.parameterVersionId,
                                                  is_hide=True)
        with allure.step("Добавление поддиаграммы в узел поддиаграммы"):
            node_sub_upd = node_update_construct(
                x=700,
                y=202,
                node_type="subdiagram",
                temp_version_id=diagram_template.versionId,
                diagram_id=subdiagram_id,
                diagram_version_id=subdiagram_version_id,
                inp_subdiagram_vars=[inp_diagram_vars],
                out_subdiagram_vars=[out_diagram_var1, out_diagram_var2],
            )
            update_node(super_user, node_id=node_sub_id, body=node_sub_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_sub_upd.nodeTypeId,
                            properties=node_sub_upd.properties))
        with allure.step("Получение информации об узле поддиаграммы"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        with allure.step("Проверка, что узел обновлён"):
            assert (
                    node_view.properties["inputVariablesMapping"][0]["nodeVariable"]
                    == subdiagram_var.parameterName
                    and len(node_view.properties["outputVariablesMapping"]) == 2
                    and node_view.properties["subdiagramId"] == subdiagram_id
                    and node_view.properties["versionId"] == subdiagram_version_id
                    and node_view.validFlag
            )

    @allure.story(
        "На вход узла возможно подать только уже существующие переменные диаграммы(расчитаны в предыдущих "
        "узлах/входящие)"
    )
    @allure.title(
        "в качестве значения входа поддиаграммы подать несуществующую переменную"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-5876")
    def test_subdiagram_put_not_input_as_input(
            self,
            super_user,
            simple_diagram,
            create_temp_start_finish_sub_int_var_linked,
    ):
        with allure.step("Создание поддиаграммы с целочисленной переменной"):
            subdiagram_version_id: ResponseDto = (
                simple_diagram[
                    "create_result"
                ]["uuid"]
            )
            subdiagram_id: ResponseDto = (
                simple_diagram["template"]["diagramId"]
            )
            subdiagram_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "diagram_param"
                ]
            )
            subdiagram_exec_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "inner_diagram_execute_var"
                ]
            )
        with allure.step("Создание диаграммы с узлом поддиаграммы"):
            diagram_template: DiagramViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_template"]
            )
            node_sub_id = create_temp_start_finish_sub_int_var_linked["node_sub_id"]
            diagram_var: DiagramInOutParameterFullViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_variable"]
            )
            inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                                  is_arr=False, is_compl=False, name=generate_string(),
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId)
            out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False,
                                                  name="diagram_execute_status", type_id="2",
                                                  node_variable="diagram_execute_status",
                                                  outer_variable_id=subdiagram_exec_var.parameterVersionId,
                                                  is_hide=True)
        with allure.step(
                "Добавление поддиаграммы в узел поддиаграммы с несуществующей входной переменной"
        ):
            node_sub_upd = node_update_construct(
                x=700,
                y=202,
                node_type="subdiagram",
                temp_version_id=diagram_template.versionId,
                diagram_id=subdiagram_id,
                diagram_version_id=subdiagram_version_id,
                inp_subdiagram_vars=[inp_diagram_vars],
                out_subdiagram_vars=[out_diagram_var1, out_diagram_var2],
            )
            update_node(super_user, node_id=node_sub_id, body=node_sub_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_sub_upd.nodeTypeId,
                            properties=node_sub_upd.properties))
        with allure.step("Получение информации об узле поддиаграммы"):
            # save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=diagram_template.diagramId,
            #                                                       versionId=diagram_template.versionId,
            #                                                       errorResponseFlag=False,
            #                                                       diagramName='check_bug',
            #                                                       diagramDescription='hello'))
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        with allure.step("Проверка, что узел невалиден"):
            assert not node_view.validFlag

    @allure.story("в version_id узла может указываться только uuid существующей диаграммы")
    @allure.title(
        "Создать диаграмму с узлом поддиаграммы с невалидным uuid диаграммы, валидация не прошла"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-5877")
    def test_create_node_subdiagram_with_subdiag_bad(
            self,
            super_user,
            simple_diagram,
            create_temp_start_finish_sub_int_var_linked,
    ):
        with allure.step("Создание поддиаграммы с целочисленной переменной"):
            subdiagram_version_id: ResponseDto = (
                simple_diagram[
                    "create_result"
                ]["uuid"]
            )
            subdiagram_id: ResponseDto = (
                simple_diagram[
                    "template"
                ]["diagramId"]
            )
            subdiagram_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "diagram_param"
                ]
            )
            subdiagram_exec_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "inner_diagram_execute_var"
                ]
            )
        with allure.step("Создание диаграммы с узлом поддиаграммы"):
            diagram_template: DiagramViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_template"]
            )
            node_sub_id = create_temp_start_finish_sub_int_var_linked["node_sub_id"]
            diagram_var: DiagramInOutParameterFullViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_variable"]
            )
            inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False,
                                                  name="diagram_execute_status", type_id="2",
                                                  node_variable="diagram_execute_status",
                                                  outer_variable_id=subdiagram_exec_var.parameterVersionId,
                                                  is_hide=True)
        with allure.step(
                "Добавление поддиаграммы в узел поддиаграммы с несуществующим uuid"
        ):
            unex_uuid = str(uuid.uuid4())
            node_sub_upd = node_update_construct(
                x=700,
                y=202,
                node_type="subdiagram",
                temp_version_id=diagram_template.versionId,
                diagram_id=unex_uuid,
                diagram_version_id=unex_uuid,
                inp_subdiagram_vars=[inp_diagram_vars],
                out_subdiagram_vars=[out_diagram_var1, out_diagram_var2],
            )
            update_node(super_user, node_id=node_sub_id, body=node_sub_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_sub_upd.nodeTypeId,
                            properties=node_sub_upd.properties))
        with allure.step("Получение информации об узле поддиаграммы"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        with allure.step("Проверка, что узел обновлён"):
            assert not node_view.validFlag

    @allure.story("Тип переменной на вход узла должен совпадать со входной переменной диаграммы"
                  "(пример typeId: в узел - 1variableName: с типом 2)(включая комплексные типы)")
    @allure.title(
        'Тип переменной на вход узла должен совпадать со входной переменной диаграммы(пример "typeId": в '
        'узел - 1"variableName": с типом 2)(включая комплексные типы)'
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-5878")
    @pytest.mark.smoke
    def test_create_node_subdiagram_with_subdiag_bad_params(
            self,
            super_user,
            simple_diagram,
            create_temp_start_finish_sub_int_var_linked,
    ):
        with allure.step("Создание поддиаграммы с целочисленной переменной"):
            subdiagram_version_id: ResponseDto = (
                simple_diagram[
                    "create_result"
                ]["uuid"]
            )
            subdiagram_id: ResponseDto = (
                simple_diagram[
                    "template"
                ]["diagramId"]
            )
            subdiagram_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "diagram_param"
                ]
            )
            subdiagram_exec_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "inner_diagram_execute_var"
                ]
            )
        with allure.step("Создание диаграммы с узлом поддиаграммы"):
            diagram_template: DiagramViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_template"]
            )
            node_sub_id = create_temp_start_finish_sub_int_var_linked["node_sub_id"]
            diagram_var: DiagramInOutParameterFullViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_variable"]
            )
        with allure.step("Подготовка несовпадающих по типу атрибутов"):
            unex_uuid = str(uuid.uuid4())
            inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="25", node_variable="a",
                                                  outer_variable_id=unex_uuid,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="44", node_variable="b",
                                                  outer_variable_id=unex_uuid,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False,
                                                  name="diagram_execute_status", type_id="2",
                                                  node_variable="diagram_execute_status",
                                                  outer_variable_id=unex_uuid,
                                                  is_hide=True)
        with allure.step(
                "Добавление поддиаграммы в узел поддиаграммы с несовпадающими по типу атрибутами"
        ):
            node_sub_upd = node_update_construct(
                x=700,
                y=202,
                node_type="subdiagram",
                temp_version_id=diagram_template.versionId,
                diagram_id=subdiagram_id,
                diagram_version_id=subdiagram_version_id,
                inp_subdiagram_vars=[inp_diagram_vars],
                out_subdiagram_vars=[out_diagram_var1, out_diagram_var2],
            )
            update_node(super_user, node_id=node_sub_id, body=node_sub_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_sub_upd.nodeTypeId,
                            properties=node_sub_upd.properties))
        with allure.step("Получение информации об узле поддиаграммы"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        with allure.step("Проверка, что узел обновлён"):
            assert not node_view.validFlag

    @allure.story("Если на выход outputVariablesMapping variableName - уникальна"
                  "(не была расчитана, не шла на вход) - после сохранения узла в get nodeid"
                  " - в nodeAddedVariables появляется эта переменная с типом соответствующим "
                  "typeId(включая комплексные типы) И в input nodes следущего узла")
    @allure.title(
        "Если на выход outputVariablesMapping variableName - уникальна(не была расчитана, не шла на вход) - после "
        "сохранения узла в get nodeid - в nodeAddedVariables появляется эта переменная с типом соответствующим "
        "typeId(включая комплексные типы) И в input nodes следущего узла"
    )
    @pytest.mark.scenario("DEV-15453")
    @pytest.mark.smoke
    def test_subdiagram_new_added_var_in_node(
            self,
            super_user,
            simple_diagram,
            create_temp_start_finish_sub_int_var_linked,
    ):
        subdiagram_new_var_check = False
        node_end_input_var_check = False
        with allure.step("Создание поддиаграммы с целочисленной переменной"):
            subdiagram_version_id: ResponseDto = (
                simple_diagram[
                    "create_result"
                ]["uuid"]
            )
            subdiagram_id: ResponseDto = (
                simple_diagram[
                    "template"
                ]["diagramId"]
            )
            subdiagram_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "diagram_param"
                ]
            )
            subdiagram_exec_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "inner_diagram_execute_var"
                ]
            )
        with allure.step("Создание диаграммы с узлом поддиаграммы"):
            diagram_template: DiagramViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_template"]
            )
            node_sub_id = create_temp_start_finish_sub_int_var_linked["node_sub_id"]
            node_end_result: ResponseDto = create_temp_start_finish_sub_int_var_linked[
                "node_end"
            ]
            diagram_var: DiagramInOutParameterFullViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_variable"]
            )
        with allure.step("Подготовка атрибутов со свежедобавленной переменной"):
            inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False, name="new_added_node_var",
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False,
                                                  name="diagram_execute_status", type_id="2",
                                                  node_variable="diagram_execute_status",
                                                  outer_variable_id=subdiagram_exec_var.parameterVersionId,
                                                  is_hide=True)
        with allure.step(
                "Добавление поддиаграммы в узел поддиаграммы с несовпадающими по типу атрибутами"
        ):
            node_sub_upd = node_update_construct(
                x=700,
                y=202,
                node_type="subdiagram",
                temp_version_id=diagram_template.versionId,
                diagram_id=subdiagram_id,
                diagram_version_id=subdiagram_version_id,
                inp_subdiagram_vars=[inp_diagram_vars],
                out_subdiagram_vars=[out_diagram_var1, out_diagram_var2],
            )
            update_node(super_user, node_id=node_sub_id, body=node_sub_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_sub_upd.nodeTypeId,
                            properties=node_sub_upd.properties))
        with allure.step("Получение информации об узле поддиаграммы"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        with allure.step("Получение информации об узле завершения"):
            node_end_view: NodeViewWithVariablesDto = (
                NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, node_end_result.uuid).body
                )
            )
        with allure.step("Проверка, что новая переменная найдена"):
            for var in node_view.availableToCalc:
                if var["variableName"] == "new_added_node_var":
                    subdiagram_new_var_check = True
            for inp_var in node_end_view.availableToMap:
                if inp_var["variableName"] == "new_added_node_var":
                    node_end_input_var_check = True
            assert subdiagram_new_var_check and node_end_input_var_check

    @allure.story("Узлу можно обновить название и описание")
    @allure.title(
        "Создать диаграмму с узлом поддиаграммы, обновить имя и описание, увидеть, что изменились"
    )
    @pytest.mark.scenario("DEV-15453")
    @pytest.mark.smoke
    def test_update_node_desc_name(
            self,
            super_user,
            simple_diagram,
            create_temp_start_finish_sub_int_var_linked,
    ):
        with allure.step("Создание поддиаграммы с целочисленной переменной"):
            subdiagram_version_id: ResponseDto = (
                simple_diagram[
                    "create_result"
                ]["uuid"]
            )
            subdiagram_id: ResponseDto = (
                simple_diagram[
                    "template"
                ]["diagramId"]
            )
            subdiagram_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "diagram_param"
                ]
            )
            subdiagram_exec_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "inner_diagram_execute_var"
                ]
            )
        with allure.step("Создание диаграммы с узлом поддиаграммы"):
            diagram_template: DiagramViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_template"]
            )
            node_sub_id = create_temp_start_finish_sub_int_var_linked["node_sub_id"]
            node_end_result: ResponseDto = create_temp_start_finish_sub_int_var_linked[
                "node_end"
            ]
            diagram_var: DiagramInOutParameterFullViewDto = (
                create_temp_start_finish_sub_int_var_linked["diagram_variable"]
            )
        with allure.step("Подготовка атрибутов со свежедобавленной переменной"):
            inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                                  type_id="1", node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False,
                                                  name="diagram_execute_status", type_id="2",
                                                  node_variable="diagram_execute_status",
                                                  outer_variable_id=subdiagram_exec_var.parameterVersionId,
                                                  is_hide=True)
        with allure.step(
                "Добавление поддиаграммы в узел поддиаграммы с несовпадающими по типу атрибутами"
        ):
            node_sub_upd = node_update_construct(
                x=700,
                y=202,
                node_type="subdiagram",
                temp_version_id=diagram_template.versionId,
                diagram_id=subdiagram_id,
                diagram_version_id=subdiagram_version_id,
                inp_subdiagram_vars=[inp_diagram_vars],
                out_subdiagram_vars=[out_diagram_var1, out_diagram_var2],
                node_name_up="Поддиаграмма_1",
                descr_up="node_updated",
            )
            update_node(super_user, node_id=node_sub_id, body=node_sub_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_sub_upd.nodeTypeId,
                            properties=node_sub_upd.properties))
        with allure.step("Получение информации об узле поддиаграммы"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        assert (
                node_view.nodeName == "Поддиаграмма_1"
                and node_view.nodeDescription == "node_updated"
        )

    @allure.story("Если на выход outputVariablesMapping variableName - уникальна"
                  "(не была расчитана, не шла на вход) и является новым атрибутом комплексного типа"
                  " - после сохранения узла в get nodeid - в nodeAddedVariables появляется эта переменная"
                  " с типом соответствующим typeId(включая комплексные типы) И в input nodes следущего узла")
    @allure.title(
        "Если на выход outputVariablesMapping variableName - уникальна(не была расчитана, не шла на вход) и является "
        "новым атрибутом комплексного типа - после сохранения узла в get nodeid - в nodeAddedVariables появляется эта "
        "переменная с типом соответствующим typeId(включая комплексные типы) И в input nodes следущего узла"
    )
    @pytest.mark.scenario("DEV-15453")
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx",
                                               varType="in", isComplex=True, isArray=False),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["поддиаграмма"])
    @pytest.mark.skip("obsolete")
    def test_subdiagram_new_added_complex_var_in_node(
            self,
            super_user,
            simple_diagram,
            diagram_constructor,
    ):
        subdiagram_new_var_check = False
        with allure.step("Создание поддиаграммы с целочисленной переменной"):
            subdiagram_version_id: ResponseDto = (
                simple_diagram[
                    "create_result"
                ]["uuid"]
            )
            subdiagram_id: ResponseDto = (
                simple_diagram[
                    "template"
                ]["diagramId"]
            )
            subdiagram_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "diagram_param"
                ]
            )
            subdiagram_exec_var: DiagramInOutParameterFullViewDto = (
                simple_diagram[
                    "inner_diagram_execute_var"
                ]
            )
        with allure.step(
                "Создание диаграммы с узлом поддиаграммы и комплексной переменной"
        ):
            diagram_template: DiagramViewDto = diagram_constructor["diagram_info"]
            node_sub_id = diagram_constructor["nodes"]["поддиаграмма"].nodeId
            node_end: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
            diagram_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
        with allure.step("Подготовка атрибутов со свежедобавленной переменной"):
            inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                                  is_arr=False, is_compl=False, name=attr.attributeName,
                                                  type_id="1",
                                                  var_path=diagram_var.parameterName,
                                                  var_root_id=diagram_var.typeId,
                                                  node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False, name=attr.attributeName,
                                                  type_id="1",
                                                  var_path=diagram_var.parameterName,
                                                  var_root_id=diagram_var.typeId,
                                                  node_variable=subdiagram_var.parameterName,
                                                  outer_variable_id=subdiagram_var.parameterVersionId,
                                                  param_id=diagram_var.parameterId)
            out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                                  is_arr=False, is_compl=False,
                                                  name="diagram_execute_status", type_id="2",
                                                  node_variable="diagram_execute_status",
                                                  outer_variable_id=subdiagram_exec_var.parameterVersionId,
                                                  is_hide=True)
        with allure.step("Добавление поддиаграммы в узел поддиаграммы"):
            node_sub_upd = node_update_construct(
                x=700,
                y=202,
                node_type="subdiagram",
                temp_version_id=diagram_template.versionId,
                diagram_id=subdiagram_id,
                diagram_version_id=subdiagram_version_id,
                inp_subdiagram_vars=[inp_diagram_vars],
                out_subdiagram_vars=[out_diagram_var1, out_diagram_var2],
            )
            update_node(super_user, node_id=node_sub_id, body=node_sub_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_sub_upd.nodeTypeId,
                            properties=node_sub_upd.properties))
        with allure.step("Получение информации об узле поддиаграммы"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body
            )
        with allure.step(
                "Проверка, что новая переменная найдена-вложенный аттрибут исходной переменной"
        ):
            for var in node_view.availableToCalc[f"{diagram_var.typeId}"]:
                if var["variableName"] == attr.attributeName:
                    subdiagram_new_var_check = True
            assert subdiagram_new_var_check
