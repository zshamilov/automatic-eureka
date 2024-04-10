import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import ResponseDto, DiagramViewDto, NodeViewShortInfo, \
    DiagramInOutParameterFullViewDto, \
    ScriptFullView, ScriptVariableFullView, DataSourceType1, DynamicListType1, CommunicationChannelFullViewDto, \
    CommunicationVariableFullViewDto, NodeValidateDto, NodeViewWithVariablesDto
from products.Decision.framework.steps.decision_steps_communication_api import get_communication_channel
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import create_node, delete_node_by_id, get_node_by_id, \
    update_node
from products.Decision.utilities.communication_constructors import communication_var_construct, communication_construct
from products.Decision.utilities.custom_models import IntNodeType, VariableParams, IntValueType
from products.Decision.utilities.node_cunstructors import empty_node_construct, comms_node_construct, \
    comm_var_construct, variables_for_node, all_node_construct, comm_node_var_construct
from products.Decision.runtime_tests.runtime_fixtures.communication_fixtures import \
    communication_consts_diagram_empty_node


@allure.epic("Диаграммы")
@allure.feature("Узел коммуникации")
class TestDiagramsCommsNode:
    @allure.story(
        "Нет ошибок, если узел корректно заполнен"
    )
    @allure.title(
        "Обновить узел коммуникации добавив к нему валидный канал коммуникации"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.nodes(["коммуникация"])
    @pytest.mark.smoke
    def test_comms_node_prim_valid(self, super_user, create_python_code_int_vars, create_communication_gen,
                                   diagram_constructor):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            script_inp_var: ScriptVariableFullView = create_python_code_int_vars["inp_var"]
            script_out_var: ScriptVariableFullView = create_python_code_int_vars["out_var"]
        with allure.step("Задание параметров канала коммуникаций"):
            channel_name = "channel_" + generate_string()
            channel_var = communication_var_construct(variable_name="comm_v",
                                                      script_var_name=script_inp_var.variableName,
                                                      primitive_type_id=script_inp_var.primitiveTypeId,
                                                      data_source_type=DataSourceType1.USER_INPUT,
                                                      dynamic_list_type=DynamicListType1.DROP_DOWN_LIST)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[channel_var],
                                           description="made_in_test")
        with allure.step("Создание канала коммуникаций"):
            create_response: ResponseDto = create_communication_gen.create_communication_channel(
                communication_channel_body=comm)
        with allure.step("Поиск канала коммуникаций по идентификатору версии"):
            channel_info = CommunicationChannelFullViewDto(
                **get_communication_channel(super_user, version_id=create_response.uuid).body)
            channel_var: CommunicationVariableFullViewDto = channel_info.communicationVariables[0]
            node_comms: NodeViewShortInfo = diagram_constructor["nodes"]["коммуникация"]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int_v"]
            temp_version_id = diagram_constructor["temp_version_id"]
        with allure.step("Обновление узла коммуникации"):
            output_var_mapping = variables_for_node(node_type="comms_out_mapping",
                                                    is_arr=False,
                                                    is_compl=False,
                                                    is_dict=False,
                                                    type_id=diagram_param_out.typeId,
                                                    node_variable=script_out_var.variableName,
                                                    name=diagram_param_out.parameterName,
                                                    outer_variable_id=script_out_var.variableId,
                                                    param_id=diagram_param_out.parameterId)
            comms_field = comm_var_construct(var_name=channel_var.variableName,
                                             var_id=str(channel_var.id),
                                             var_value=5,
                                             data_source_type=channel_var.dataSourceType,
                                             dynamic_list_type=channel_var.dynamicListType,
                                             type_id=channel_var.primitiveTypeId,
                                             display_name=channel_var.variableName)
            node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                         chanel_id=str(channel_info.communicationChannelId),
                                                         chanel_vers_id=str(channel_info.versionId),
                                                         comms_vars=[comms_field],
                                                         output_var_mapps=[output_var_mapping])
            update_body = all_node_construct(x=700, y=202.22915649414062,
                                             node_id=str(node_comms.nodeId),
                                             temp_version_id=temp_version_id,
                                             node_name=node_comms.nodeName,
                                             int_node_type=node_comms.nodeTypeId,
                                             properties=node_comms_properties,
                                             operation="update")
            update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_comms.nodeId).body
            )
            assert node_view.properties["channelVersionId"] == str(channel_info.versionId) and \
                   node_view.validFlag

    @allure.story("Узел коммуникации создаётся")
    @allure.title(
        "Создать диаграмму с узлом коммуникации без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-537")
    @pytest.mark.smoke
    def test_create_node_comms(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла коммуникации"):
            node_comms = empty_node_construct(
                x=700, y=202.22915649414062, node_type=IntNodeType.communication,
                diagram_version_id=temp_version_id, node_name="коммуникация"
            )
            node_comms_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_comms).body
            )
            node_comms_id = node_comms_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла корректен и равен коммуникации"
        ):
            assert diagram.nodes[str(node_comms_id)].nodeTypeId == IntNodeType.communication

    @allure.story("Узел коммуникации удаляется")
    @allure.title(
        "Создать диаграмму с узлом коммуникации без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.scenario("DEV-537")
    @pytest.mark.smoke
    def test_delete_node_comms(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла коммуникации"):
            node_comms = empty_node_construct(
                x=700, y=202.22915649414062, node_type=IntNodeType.communication,
                diagram_version_id=temp_version_id, node_name="коммуникация"
            )
            node_comms_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_comms).body
            )
            node_comms_id = node_comms_response.uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_comms_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert get_node_by_id(super_user, node_comms_id)

    @allure.story(
        "Нет ошибок, если передать константы в переменных диаграммы в Коммуникации"
    )
    @allure.title(
        "Обновить узел коммуникации добавив к нему валидный канал коммуникации"
    )
    @pytest.mark.variable_data(
        [VariableParams(varName="out1", varType="out", varDataType=IntValueType.bool.value),
         VariableParams(varName="out2", varType="out", varDataType=IntValueType.date.value),
         VariableParams(varName="out3", varType="out", varDataType=IntValueType.time.value),
         VariableParams(varName="out4", varType="out", varDataType=IntValueType.dateTime.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["коммуникация"])
    @pytest.mark.smoke
    def test_comms_node_const_valid(self, super_user, communication_consts_diagram_empty_node):
        channel_vars: list[CommunicationVariableFullViewDto] = communication_consts_diagram_empty_node["channel_vars"]
        script_out_vars: list[ScriptVariableFullView] = communication_consts_diagram_empty_node["script_out_vars"]

        node_comms: NodeViewShortInfo = communication_consts_diagram_empty_node["nodes"]["коммуникация"]
        channel_info: CommunicationChannelFullViewDto = communication_consts_diagram_empty_node["channel_info"]
        diagram_param_out_bool: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
            "variables"]["out1"]
        diagram_param_out_date: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
            "variables"]["out2"]
        diagram_param_out_time: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
            "variables"]["out3"]
        diagram_param_out_date_time: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
            "variables"]["out4"]
        diagram_vars = [diagram_param_out_bool, diagram_param_out_date, diagram_param_out_time,
                        diagram_param_out_date_time]
        temp_version_id = communication_consts_diagram_empty_node["temp_version_id"]

        with allure.step("Обновление узла коммуникации"):
            with allure.step("Заполнение маппинга выходных переменных узла"):
                out_v_map = []
                for script_v in script_out_vars:
                    for diagram_v in diagram_vars:
                        if diagram_v.typeId == script_v.primitiveTypeId:
                            out_v_map.append(variables_for_node(node_type="comms_out_mapping",
                                                                is_arr=False,
                                                                is_compl=False,
                                                                is_dict=False,
                                                                type_id=diagram_v.typeId,
                                                                node_variable=script_v.variableName,
                                                                name=diagram_v.parameterName,
                                                                outer_variable_id=script_v.variableId,
                                                                param_id=diagram_v.parameterId))
                            break
            with allure.step("Заполнение маппинга переменных коммуникации"):
                comms_map = []
                for comms_v in channel_vars:
                    var_name = ""
                    if comms_v.primitiveTypeId == IntValueType.float.value:
                        var_name = "9.1"
                    elif comms_v.primitiveTypeId == IntValueType.int.value:
                        var_name = "666"
                    elif comms_v.primitiveTypeId == IntValueType.str.value:
                        var_name = "'line'"
                    elif comms_v.primitiveTypeId == IntValueType.bool.value:
                        var_name = "'true'"
                    elif comms_v.primitiveTypeId == IntValueType.date.value:
                        var_name = "'2023-12-22'"
                    elif comms_v.primitiveTypeId == IntValueType.dateTime.value:
                        var_name = "'2023-12-22 01:01:01.434'"
                    elif comms_v.primitiveTypeId == IntValueType.time.value:
                        var_name = "'01:01:01'"
                    elif comms_v.primitiveTypeId == IntValueType.long.value:
                        var_name = "7"
                    comms_map.append(comm_node_var_construct(var_name=var_name,
                                                             var_id=str(comms_v.id),
                                                             type_id=comms_v.primitiveTypeId,
                                                             param_id=None,
                                                             is_literal=True,
                                                             node_variable=comms_v.variableName))

            node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                         chanel_id=str(channel_info.communicationChannelId),
                                                         chanel_vers_id=str(channel_info.versionId),
                                                         comms_vars=[],
                                                         node_var_mapps=comms_map,
                                                         output_var_mapps=out_v_map)
            update_body = all_node_construct(x=700, y=202.22915649414062,
                                             node_id=str(node_comms.nodeId),
                                             temp_version_id=temp_version_id,
                                             node_name=node_comms.nodeName,
                                             int_node_type=node_comms.nodeTypeId,
                                             properties=node_comms_properties,
                                             operation="update")
            update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_comms.nodeId).body)
        with allure.step("Узел валиден, константы проставились"):
            assert node_view.properties["channelVersionId"] == str(channel_info.versionId)
            assert node_view.validFlag
            assert all(v["isLiteral"] for v in node_view.properties["nodeVariablesMapping"])

    @allure.story(
        "Есть ошибки вылидации, если передать не верно заданные константы в переменных диаграммы в Коммуникации"
    )
    @allure.title(
        "Обновить узел коммуникации добавив к нему валидный канал коммуникации,"
        " в маппинге переменных диаграммы  использовать константы"
    )
    @pytest.mark.variable_data(
        [VariableParams(varName="out1", varType="out", varDataType=IntValueType.bool.value),
         VariableParams(varName="out2", varType="out", varDataType=IntValueType.date.value),
         VariableParams(varName="out3", varType="out", varDataType=IntValueType.time.value),
         VariableParams(varName="out4", varType="out", varDataType=IntValueType.dateTime.value),
         VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["коммуникация"])
    @pytest.mark.smoke
    def test_comms_node_const_not_valid(self, super_user, communication_consts_diagram_empty_node):
        with allure.step("Получение информации о входных переменных канала"):
            channel_vars: list[CommunicationVariableFullViewDto] = communication_consts_diagram_empty_node[
                "channel_vars"]
            script_out_vars: list[ScriptVariableFullView] = communication_consts_diagram_empty_node["script_out_vars"]
        with allure.step("Получение информации о канале, шаблоне, узле Коммуникации и выходных переменных диаграммы"):
            node_comms: NodeViewShortInfo = communication_consts_diagram_empty_node["nodes"]["коммуникация"]
            channel_info: CommunicationChannelFullViewDto = communication_consts_diagram_empty_node["channel_info"]
            temp_version_id = communication_consts_diagram_empty_node["temp_version_id"]
            diagram_param_out_bool: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
                "variables"]["out1"]
            diagram_param_out_date: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
                "variables"]["out2"]
            diagram_param_out_time: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
                "variables"]["out3"]
            diagram_param_out_date_time: DiagramInOutParameterFullViewDto = communication_consts_diagram_empty_node[
                "variables"]["out4"]
            diagram_vars = [diagram_param_out_bool, diagram_param_out_date, diagram_param_out_time,
                            diagram_param_out_date_time]
        with allure.step("Обновление узла коммуникации, константы задаем неверно"):
            with allure.step("Обновление узла коммуникации"):
                with allure.step("Заполнение маппинга выходных переменных узла"):
                    out_v_map = []
                    for script_v in script_out_vars:
                        for diagram_v in diagram_vars:
                            if diagram_v.typeId == script_v.primitiveTypeId:
                                out_v_map.append(variables_for_node(node_type="comms_out_mapping",
                                                                    is_arr=False,
                                                                    is_compl=False,
                                                                    is_dict=False,
                                                                    type_id=diagram_v.typeId,
                                                                    node_variable=script_v.variableName,
                                                                    name=diagram_v.parameterName,
                                                                    outer_variable_id=script_v.variableId,
                                                                    param_id=diagram_v.parameterId))
                                break
            with allure.step("Заполнение маппинга невалидных нечисловых констант на переменные коммуникации"):
                comms_map = []
                for comms_v in channel_vars:
                    var_name = ""
                    if comms_v.primitiveTypeId == IntValueType.float.value:
                        var_name = "9.1"
                    elif comms_v.primitiveTypeId == IntValueType.int.value:
                        var_name = "666"
                    elif comms_v.primitiveTypeId == IntValueType.str.value:
                        # Невалидное значение - нет кавычек дополнительных
                        var_name = "line"
                    elif comms_v.primitiveTypeId == IntValueType.bool.value:
                        # Невалидное значение - нет кавычек дополнительных
                        var_name = "true"
                    elif comms_v.primitiveTypeId == IntValueType.date.value:
                        # Невалидное значение - нет кавычек дополнительных
                        var_name = "2023-12-22"
                    elif comms_v.primitiveTypeId == IntValueType.dateTime.value:
                        # Невалидное значение - нет кавычек дополнительных
                        var_name = "2023-12-22 01:01:01.434"
                    elif comms_v.primitiveTypeId == IntValueType.time.value:
                        # Невалидное значение - нет кавычек дополнительных
                        var_name = "01:01:01"
                    elif comms_v.primitiveTypeId == IntValueType.long.value:
                        var_name = "7"
                    comms_map.append(comm_node_var_construct(var_name=var_name,
                                                             var_id=str(comms_v.id),
                                                             type_id=comms_v.primitiveTypeId,
                                                             param_id=None,
                                                             is_literal=True,
                                                             node_variable=comms_v.variableName))

            node_comms_properties = comms_node_construct(chanel_name=channel_info.objectName,
                                                         chanel_id=str(channel_info.communicationChannelId),
                                                         chanel_vers_id=str(channel_info.versionId),
                                                         comms_vars=[],
                                                         node_var_mapps=comms_map,
                                                         output_var_mapps=out_v_map)
            update_body = all_node_construct(x=700, y=202.22915649414062,
                                             node_id=str(node_comms.nodeId),
                                             temp_version_id=temp_version_id,
                                             node_name=node_comms.nodeName,
                                             int_node_type=node_comms.nodeTypeId,
                                             properties=node_comms_properties,
                                             operation="update")
            update_node(super_user, node_id=node_comms.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_comms.nodeId).body)
        with allure.step("Узел не валиден, константы заданы неверно"):
            assert all([k["variableName"] == "Константа задана неверно" for k in node_view.validationPayload
            ["nodeValidationMap"]["nodeVariablesMapping"].values()])
            assert len(node_view.validationPayload["nodeValidationMap"]["nodeVariablesMapping"].values()) == 6
            assert not node_view.validFlag
