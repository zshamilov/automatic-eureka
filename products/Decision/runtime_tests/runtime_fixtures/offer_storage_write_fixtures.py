import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import NodeViewShortInfo, ExternalServiceTechFullViewDto, \
    DiagramInOutParameterFullViewDto, \
    NodeViewWithVariablesDto, NodeUpdateDto, DiagramViewDto, VariableType1, ScriptFullView, DataSourceType, ResponseDto, \
    OfferFullViewDto, ScriptVariableFullView
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_external_service_api import get_tech_service
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.framework.steps.decision_steps_offer_api import get_offer_info
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.node_cunstructors import variables_for_node, offer_properties, \
    node_update_construct, offer_node_construct
from products.Decision.utilities.offer_constructors import offer_variable_construct, offer_construct
from products.Decision.utilities.offer_storage_node_constructors import os_write_construct


@pytest.fixture()
def offer_storage_write_without_flag(super_user, diagram_constructor, save_diagrams_gen):
    """
    Фикстура для создания диаграммы с настроенным узлом Отправка предложений в Offer Storage без флага продолжить
    работу диаграммы при частичной записи предложений
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_os_write: NodeViewShortInfo = diagram_constructor["nodes"]["запись OS"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
        **get_tech_service(super_user, node_type="OFFER_STORAGE_WRITE").body[0])
    variable_for_offer: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_offers"]
    node_os_up_data = os_write_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                         output_var_name=variable_for_offer.parameterName,
                                         output_var_type_id=variable_for_offer.typeId,
                                         service_id=tech_service.serviceId,
                                         service_version_id=tech_service.versionId,
                                         param_id=variable_for_offer.parameterId)
    update_node(super_user, node_id=node_os_write.nodeId, body=node_os_up_data)
    node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_finish.nodeId).body)
    finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                             diagramVersionId=temp_vers_id,
                                             nodeName=node_finish_info.nodeName,
                                             nodeDescription=node_finish_info.nodeDescription,
                                             properties=node_finish_info.properties,
                                             metaInfo=node_finish_info.metaInfo, validFlag=True)
    update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)
    new_diagram_name = "ag_test_diagram_os_read" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def offer_storage_write_with_offer_and_calc(super_user, diagram_constructor, save_diagrams_gen, create_code_gen,
                                            create_offer_gen, request):
    """
    Фикстура для создания диаграммы с настроенными узломи, расположенными друг за другом: предложение -> Отправка
    предложений в Offer Storage без флага продолжить работу диаграммы при частичной записи предложений -> расчет
    переменной
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_os_write: NodeViewShortInfo = diagram_constructor["nodes"]["запись OS"]
    node_offer: NodeViewShortInfo = diagram_constructor["nodes"]["предложение"]
    node_calc: NodeViewShortInfo = diagram_constructor["nodes"]["расчет переменной"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    variable_for_offer: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_offers"]
    input_vars_product_code: DiagramInOutParameterFullViewDto = diagram_constructor["variables"][
        "in_offer_product_code"]
    input_vars_offer_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_offer_id"]
    input_vars_client_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_client_id"]
    input_vars_client_id_type: DiagramInOutParameterFullViewDto = diagram_constructor["variables"][
        "in_offer_client_id_type"]
    input_vars_control_group: DiagramInOutParameterFullViewDto = diagram_constructor["variables"][
        "in_offer_control_group"]
    input_vars_score: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_score"]
    input_vars_start_at: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_start_at"]
    input_vars_end_at: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_end_at"]
    diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int"]
    continue_flg_marker = request.node.get_closest_marker("continue_flg")
    with allure.step("Создание скрипта"):
        script_inp_var_product_code = script_vars_construct(var_name="in_product_code",
                                                            var_type=VariableType1.IN,
                                                            is_array=False, primitive_id="2")
        script_inp_var_offer_id = script_vars_construct(var_name="in_offer_id",
                                                        var_type=VariableType1.IN,
                                                        is_array=False, primitive_id="2")
        script_inp_var_client_id = script_vars_construct(var_name="in_client_id",
                                                         var_type=VariableType1.IN,
                                                         is_array=False, primitive_id="2")
        script_inp_var_client_id_type = script_vars_construct(var_name="in_client_id_type",
                                                              var_type=VariableType1.IN,
                                                              is_array=False, primitive_id="2")
        script_inp_var_control_group = script_vars_construct(var_name="in_control_group",
                                                             var_type=VariableType1.IN,
                                                             is_array=False, primitive_id="4")
        script_inp_var_score = script_vars_construct(var_name="in_offer_score",
                                                     var_type=VariableType1.IN,
                                                     is_array=False, primitive_id="0")
        script_inp_var_start_at = script_vars_construct(var_name="in_start_at",
                                                        var_type=VariableType1.IN,
                                                        is_array=False, primitive_id="2")
        script_inp_var_end_at = script_vars_construct(var_name="in_end_at",
                                                      var_type=VariableType1.IN,
                                                      is_array=False, primitive_id="2")
        script_out_var = script_vars_construct(var_name="output_offers",
                                               var_type=VariableType1.OUT,
                                               is_array=True, complex_vers_id=variable_for_offer.typeId)
        script_text = "import java.util.UUID;\n" \
                      "def offer = [" \
                      f"\"offerId\": {script_inp_var_offer_id.variableName}, " \
                      f"\n\"clientId\": {script_inp_var_client_id.variableName}, " \
                      f"\n\"clientIdType\": {script_inp_var_client_id_type.variableName}, " \
                      f"\n\"controlGroup\": {script_inp_var_control_group.variableName}," \
                      f"\n\"productCode\": {script_inp_var_product_code.variableName}," \
                      f"\n\"score\": {script_inp_var_score.variableName}," \
                      f"\n\"startAt\": {script_inp_var_start_at.variableName}," \
                      f"\n\"endAt\": {script_inp_var_end_at.variableName}]" \
                      "\noutput_offers = [offer]"
        script_name = "ag_groovy_script_" + generate_string()
        groovy_code_create_result = create_code_gen.create_groovy_code(script_text, script_name, variables=[
            script_inp_var_product_code,
            script_inp_var_offer_id,
            script_inp_var_client_id,
            script_inp_var_client_id_type,
            script_inp_var_control_group,
            script_inp_var_score,
            script_inp_var_start_at,
            script_inp_var_end_at,
            script_out_var])
        script_view: ScriptFullView = groovy_code_create_result["code_create_result"]
        script_inp_var_product_code_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_product_code.variableName]
        script_inp_var_offer_id_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_offer_id.variableName]
        script_inp_var_client_id_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_client_id.variableName]
        script_inp_var_client_id_type_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_client_id_type.variableName]
        script_inp_var_control_group_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_control_group.variableName]
        script_inp_var_score_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_score.variableName]
        script_inp_var_start_at_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_start_at.variableName]
        script_inp_var_end_at_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_end_at.variableName]
        script_out_var_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_out_var.variableName]
    with allure.step("Создание предложения"):
        offer_var_product_code = offer_variable_construct(variable_name="product_code",
                                                          script_variable_name=script_inp_var_product_code_with_id.variableName,
                                                          array_flag=False,
                                                          data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                          mandatory_flag=False,
                                                          primitive_type_id="2")
        offer_var_offer_id = offer_variable_construct(variable_name="offer_id",
                                                      script_variable_name=script_inp_var_offer_id_with_id.variableName,
                                                      array_flag=False,
                                                      data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                      mandatory_flag=False,
                                                      primitive_type_id="2")
        offer_var_client_id = offer_variable_construct(variable_name="client_id",
                                                       script_variable_name=script_inp_var_client_id_with_id.variableName,
                                                       array_flag=False,
                                                       data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                       mandatory_flag=False,
                                                       primitive_type_id="2")
        offer_var_client_id_type = offer_variable_construct(variable_name="client_id_type",
                                                            script_variable_name=script_inp_var_client_id_type_with_id.variableName,
                                                            array_flag=False,
                                                            data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                            mandatory_flag=False,
                                                            primitive_type_id="2")
        offer_var_control_group = offer_variable_construct(variable_name="control_group",
                                                           script_variable_name=script_inp_var_control_group_with_id.variableName,
                                                           array_flag=False,
                                                           data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                           mandatory_flag=False,
                                                           primitive_type_id="4")
        offer_var_score = offer_variable_construct(variable_name="score",
                                                   script_variable_name=script_inp_var_score_with_id.variableName,
                                                   array_flag=False,
                                                   data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                   mandatory_flag=False,
                                                   primitive_type_id="0")
        offer_var_start_at = offer_variable_construct(variable_name="start_at",
                                                      script_variable_name=script_inp_var_start_at_with_id.variableName,
                                                      array_flag=False,
                                                      data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                      mandatory_flag=False,
                                                      primitive_type_id="2")
        offer_var_end_at = offer_variable_construct(variable_name="end_at",
                                                    script_variable_name=script_inp_var_end_at_with_id.variableName,
                                                    array_flag=False,
                                                    data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                    mandatory_flag=False,
                                                    primitive_type_id="2")
        offer_name = "test_ag_offer_" + generate_string()
        offer = offer_construct(offer_name=offer_name,
                                script_version_id=script_view.versionId,
                                script_id=script_view.scriptId,
                                script_name=script_view.objectName,
                                offer_complex_type_version_id=variable_for_offer.typeId,
                                offer_variables=[offer_var_product_code, offer_var_offer_id, offer_var_client_id,
                                                 offer_var_client_id_type, offer_var_control_group, offer_var_score,
                                                 offer_var_start_at, offer_var_end_at])
        create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
        search_response = OfferFullViewDto(**get_offer_info(super_user, create_response.uuid).body)
        offer_vars_with_id: dict[str, OfferFullViewDto] = {}
        for var in search_response.offerVariables:
            offer_vars_with_id[var.variableName] = var
    with allure.step("Обновление узла предложение"):
        offer_node_var_map_product_code = variables_for_node(node_type="offer_mapping",
                                                             is_arr=False,
                                                             is_compl=False,
                                                             is_dict=False,
                                                             type_id=offer_var_product_code.primitiveTypeId,
                                                             node_variable=offer_var_product_code.variableName,
                                                             name=input_vars_product_code.parameterName,
                                                             outer_variable_id=str(offer_vars_with_id[
                                                                                       offer_var_product_code.variableName].id),
                                                             param_id=input_vars_product_code.parameterId)
        offer_node_var_map_offer_id = variables_for_node(node_type="offer_mapping",
                                                         is_arr=False,
                                                         is_compl=False,
                                                         is_dict=False,
                                                         type_id=offer_var_offer_id.primitiveTypeId,
                                                         node_variable=offer_var_offer_id.variableName,
                                                         name=input_vars_offer_id.parameterName,
                                                         outer_variable_id=str(
                                                             offer_vars_with_id[offer_var_offer_id.variableName].id),
                                                         param_id=input_vars_offer_id.parameterId)
        offer_node_var_map_client_id = variables_for_node(node_type="offer_mapping",
                                                          is_arr=False,
                                                          is_compl=False,
                                                          is_dict=False,
                                                          type_id=offer_var_client_id.primitiveTypeId,
                                                          node_variable=offer_var_client_id.variableName,
                                                          name=input_vars_client_id.parameterName,
                                                          outer_variable_id=str(
                                                              offer_vars_with_id[offer_var_client_id.variableName].id),
                                                          param_id=input_vars_client_id.parameterId)
        offer_node_var_map_client_id_type = variables_for_node(node_type="offer_mapping",
                                                               is_arr=False,
                                                               is_compl=False,
                                                               is_dict=False,
                                                               type_id=offer_var_client_id_type.primitiveTypeId,
                                                               node_variable=offer_var_client_id_type.variableName,
                                                               name=input_vars_client_id_type.parameterName,
                                                               outer_variable_id=str(offer_vars_with_id[
                                                                                         offer_var_client_id_type.variableName].id),
                                                               param_id=input_vars_client_id_type.parameterId)
        offer_node_var_map_control_group = variables_for_node(node_type="offer_mapping",
                                                              is_arr=False,
                                                              is_compl=False,
                                                              is_dict=False,
                                                              type_id=offer_var_control_group.primitiveTypeId,
                                                              node_variable=offer_var_control_group.variableName,
                                                              name=input_vars_control_group.parameterName,
                                                              outer_variable_id=str(offer_vars_with_id[
                                                                                        offer_var_control_group.variableName].id),
                                                              param_id=input_vars_control_group.parameterId)
        offer_node_var_map_score = variables_for_node(node_type="offer_mapping",
                                                      is_arr=False,
                                                      is_compl=False,
                                                      is_dict=False,
                                                      type_id=offer_var_score.primitiveTypeId,
                                                      node_variable=offer_var_score.variableName,
                                                      name=input_vars_score.parameterName,
                                                      outer_variable_id=str(
                                                          offer_vars_with_id[offer_var_score.variableName].id),
                                                      param_id=input_vars_score.parameterId)
        offer_node_var_map_start_at = variables_for_node(node_type="offer_mapping",
                                                         is_arr=False,
                                                         is_compl=False,
                                                         is_dict=False,
                                                         type_id=offer_var_start_at.primitiveTypeId,
                                                         node_variable=offer_var_start_at.variableName,
                                                         name=input_vars_start_at.parameterName,
                                                         outer_variable_id=str(
                                                             offer_vars_with_id[offer_var_start_at.variableName].id),
                                                         param_id=input_vars_start_at.parameterId)
        offer_node_var_map_end_at = variables_for_node(node_type="offer_mapping",
                                                       is_arr=False,
                                                       is_compl=False,
                                                       is_dict=False,
                                                       type_id=offer_var_end_at.primitiveTypeId,
                                                       node_variable=offer_var_end_at.variableName,
                                                       name=input_vars_end_at.parameterName,
                                                       outer_variable_id=str(
                                                           offer_vars_with_id[offer_var_end_at.variableName].id),
                                                       param_id=input_vars_end_at.parameterId)
        offer_output_var_mapping = variables_for_node(node_type="offer_output",
                                                      is_arr=True,
                                                      is_compl=True,
                                                      is_dict=False,
                                                      type_id=variable_for_offer.typeId,
                                                      node_variable=variable_for_offer.parameterName,
                                                      name=variable_for_offer.parameterName,
                                                      param_id=variable_for_offer.parameterId)
        offer_node_properties = offer_properties(offer_id=str(search_response.id),
                                                 offer_version_id=str(search_response.versionId),
                                                 offer_variables=[],
                                                 node_variables_mapping=[offer_node_var_map_product_code,
                                                                         offer_node_var_map_offer_id,
                                                                         offer_node_var_map_client_id,
                                                                         offer_node_var_map_client_id_type,
                                                                         offer_node_var_map_control_group,
                                                                         offer_node_var_map_score,
                                                                         offer_node_var_map_start_at,
                                                                         offer_node_var_map_end_at],
                                                 output_variable_mapping=offer_output_var_mapping)
        offer_update_body = offer_node_construct(x=700, y=202.22915649414062,
                                                 temp_version_id=temp_vers_id,
                                                 properties=offer_node_properties,
                                                 operation="update",
                                                 node_id=str(node_offer.nodeId))
        update_node(super_user, node_id=node_offer.nodeId, body=offer_update_body)
    with allure.step("Обновление узла отправка предложений в OS"):
        tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
            **get_tech_service(super_user, node_type="OFFER_STORAGE_WRITE").body[0])
        if continue_flg_marker is not None:
            continue_var = continue_flg_marker.args[0]
        else:
            continue_var = False
        node_os_up_data = os_write_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                             output_var_name=variable_for_offer.parameterName,
                                             output_var_type_id=variable_for_offer.typeId,
                                             service_id=tech_service.serviceId,
                                             service_version_id=tech_service.versionId,
                                             continue_flg=continue_var,
                                             param_id=variable_for_offer.parameterId)
        update_node(super_user, node_id=node_os_write.nodeId, body=node_os_up_data)
    with allure.step("Обновление узла расчет переменных"):
        calc_vars_node = variables_for_node(
            node_type="var_calc",
            is_arr=False,
            is_compl=False,
            name=diagram_param_out.parameterName,
            type_id=diagram_param_out.typeId,
            calc_val="5",
            calc_type_id="2",
            param_id=diagram_param_out.parameterId
        )
        calc_node_upd = node_update_construct(
            700,
            202.22915649414062,
            "var_calc",
            temp_vers_id,
            [calc_vars_node],
        )
        update_node(super_user, node_id=node_calc.nodeId, body=calc_node_upd)
    with allure.step("Обновление узла завершение"):
        node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_finish.nodeId).body)
        finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                                 diagramVersionId=temp_vers_id,
                                                 nodeName=node_finish_info.nodeName,
                                                 nodeDescription=node_finish_info.nodeDescription,
                                                 properties=node_finish_info.properties,
                                                 metaInfo=node_finish_info.metaInfo, validFlag=True)
        update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)

    new_diagram_name = "ag_test_diagram_os_read" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}


@pytest.fixture()
def offer_storage_write_with_offer(super_user, diagram_constructor, save_diagrams_gen, create_code_gen,
                                   create_offer_gen, request):
    """
    Фикстура для создания диаграммы с настроенными узломи, расположенными друг за другом: предложение -> Отправка
    предложений в Offer Storage без флага продолжить работу диаграммы при частичной записи предложений
    """
    temp_vers_id = diagram_constructor["temp_version_id"]
    diagram_id = diagram_constructor["diagram_id"]
    node_os_write: NodeViewShortInfo = diagram_constructor["nodes"]["запись OS"]
    node_offer: NodeViewShortInfo = diagram_constructor["nodes"]["предложение"]
    node_finish: NodeViewShortInfo = diagram_constructor["nodes"]["завершение"]
    variable_for_offer: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_offers"]
    input_vars_product_code: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_product_code"]
    input_vars_offer_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_offer_id"]
    input_vars_client_id: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_client_id"]
    input_vars_client_id_type: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_client_id_type"]
    input_vars_control_group: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_control_group"]
    input_vars_score: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_score"]
    input_vars_start_at: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_start_at"]
    input_vars_end_at: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_offer_end_at"]
    continue_flg_marker = request.node.get_closest_marker("continue_flg")
    with allure.step("Создание скрипта"):
        script_inp_var_product_code = script_vars_construct(var_name="in_product_code",
                                                            var_type=VariableType1.IN,
                                                            is_array=False, primitive_id="2")
        script_inp_var_offer_id = script_vars_construct(var_name="in_offer_id",
                                                        var_type=VariableType1.IN,
                                                        is_array=False, primitive_id="2")
        script_inp_var_client_id = script_vars_construct(var_name="in_client_id",
                                                         var_type=VariableType1.IN,
                                                         is_array=False, primitive_id="2")
        script_inp_var_client_id_type = script_vars_construct(var_name="in_client_id_type",
                                                              var_type=VariableType1.IN,
                                                              is_array=False, primitive_id="2")
        script_inp_var_control_group = script_vars_construct(var_name="in_control_group",
                                                             var_type=VariableType1.IN,
                                                             is_array=False, primitive_id="4")
        script_inp_var_score = script_vars_construct(var_name="in_offer_score",
                                                     var_type=VariableType1.IN,
                                                     is_array=False, primitive_id="0")
        script_inp_var_start_at = script_vars_construct(var_name="in_start_at",
                                                        var_type=VariableType1.IN,
                                                        is_array=False, primitive_id="2")
        script_inp_var_end_at = script_vars_construct(var_name="in_end_at",
                                                      var_type=VariableType1.IN,
                                                      is_array=False, primitive_id="2")
        script_out_var = script_vars_construct(var_name="output_offers",
                                               var_type=VariableType1.OUT,
                                               is_array=True, complex_vers_id=variable_for_offer.typeId)
        script_text = "import java.util.UUID;\n" \
                      "def offer = [" \
                      f"\"offerId\": {script_inp_var_offer_id.variableName}, " \
                      f"\n\"clientId\": {script_inp_var_client_id.variableName}, " \
                      f"\n\"clientIdType\": {script_inp_var_client_id_type.variableName}, " \
                      f"\n\"controlGroup\": {script_inp_var_control_group.variableName}," \
                      f"\n\"productCode\": {script_inp_var_product_code.variableName}," \
                      f"\n\"score\": {script_inp_var_score.variableName}," \
                      f"\n\"startAt\": {script_inp_var_start_at.variableName}," \
                      f"\n\"endAt\": {script_inp_var_end_at.variableName}]" \
                      "\noutput_offers = [offer]"
        script_name = "ag_groovy_script_" + generate_string()
        groovy_code_create_result = create_code_gen.create_groovy_code(script_text, script_name, variables=[
            script_inp_var_product_code,
            script_inp_var_offer_id,
            script_inp_var_client_id,
            script_inp_var_client_id_type,
            script_inp_var_control_group,
            script_inp_var_score,
            script_inp_var_start_at,
            script_inp_var_end_at,
            script_out_var])
        script_view: ScriptFullView = groovy_code_create_result["code_create_result"]
        script_inp_var_product_code_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_product_code.variableName]
        script_inp_var_offer_id_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_offer_id.variableName]
        script_inp_var_client_id_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_client_id.variableName]
        script_inp_var_client_id_type_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_client_id_type.variableName]
        script_inp_var_control_group_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_control_group.variableName]
        script_inp_var_score_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_score.variableName]
        script_inp_var_start_at_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_start_at.variableName]
        script_inp_var_end_at_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_inp_var_end_at.variableName]
        script_out_var_with_id: ScriptVariableFullView = groovy_code_create_result["variables_with_ids"][
            script_out_var.variableName]
    with allure.step("Создание предложения"):
        offer_var_product_code = offer_variable_construct(variable_name="product_code",
                                                          script_variable_name=script_inp_var_product_code_with_id.variableName,
                                                          array_flag=False,
                                                          data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                          mandatory_flag=False,
                                                          primitive_type_id="2")
        offer_var_offer_id = offer_variable_construct(variable_name="offer_id",
                                                      script_variable_name=script_inp_var_offer_id_with_id.variableName,
                                                      array_flag=False,
                                                      data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                      mandatory_flag=False,
                                                      primitive_type_id="2")
        offer_var_client_id = offer_variable_construct(variable_name="client_id",
                                                       script_variable_name=script_inp_var_client_id_with_id.variableName,
                                                       array_flag=False,
                                                       data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                       mandatory_flag=False,
                                                       primitive_type_id="2")
        offer_var_client_id_type = offer_variable_construct(variable_name="client_id_type",
                                                            script_variable_name=script_inp_var_client_id_type_with_id.variableName,
                                                            array_flag=False,
                                                            data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                            mandatory_flag=False,
                                                            primitive_type_id="2")
        offer_var_control_group = offer_variable_construct(variable_name="control_group",
                                                           script_variable_name=script_inp_var_control_group_with_id.variableName,
                                                           array_flag=False,
                                                           data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                           mandatory_flag=False,
                                                           primitive_type_id="4")
        offer_var_score = offer_variable_construct(variable_name="score",
                                                   script_variable_name=script_inp_var_score_with_id.variableName,
                                                   array_flag=False,
                                                   data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                   mandatory_flag=False,
                                                   primitive_type_id="0")
        offer_var_start_at = offer_variable_construct(variable_name="start_at",
                                                      script_variable_name=script_inp_var_start_at_with_id.variableName,
                                                      array_flag=False,
                                                      data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                      mandatory_flag=False,
                                                      primitive_type_id="2")
        offer_var_end_at = offer_variable_construct(variable_name="end_at",
                                                    script_variable_name=script_inp_var_end_at_with_id.variableName,
                                                    array_flag=False,
                                                    data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                    mandatory_flag=False,
                                                    primitive_type_id="2")
        offer_name = "test_ag_offer_" + generate_string()
        offer = offer_construct(offer_name=offer_name,
                                script_version_id=script_view.versionId,
                                script_id=script_view.scriptId,
                                script_name=script_view.objectName,
                                offer_complex_type_version_id=variable_for_offer.typeId,
                                offer_variables=[offer_var_product_code, offer_var_offer_id, offer_var_client_id,
                                                 offer_var_client_id_type, offer_var_control_group, offer_var_score,
                                                 offer_var_start_at, offer_var_end_at])
        create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
        search_response = OfferFullViewDto(**get_offer_info(super_user, create_response.uuid).body)
        offer_vars_with_id: dict[str, OfferFullViewDto] = {}
        for var in search_response.offerVariables:
            offer_vars_with_id[var.variableName] = var
    with allure.step("Обновление узла предложение"):
        offer_node_var_map_product_code = variables_for_node(node_type="offer_mapping",
                                                             is_arr=False,
                                                             is_compl=False,
                                                             is_dict=False,
                                                             type_id=offer_var_product_code.primitiveTypeId,
                                                             node_variable=offer_var_product_code.variableName,
                                                             name=input_vars_product_code.parameterName,
                                                             outer_variable_id=str(offer_vars_with_id[
                                                                                       offer_var_product_code.variableName].id),
                                                             param_id=input_vars_product_code.parameterId)
        offer_node_var_map_offer_id = variables_for_node(node_type="offer_mapping",
                                                         is_arr=False,
                                                         is_compl=False,
                                                         is_dict=False,
                                                         type_id=offer_var_offer_id.primitiveTypeId,
                                                         node_variable=offer_var_offer_id.variableName,
                                                         name=input_vars_offer_id.parameterName,
                                                         outer_variable_id=str(
                                                             offer_vars_with_id[offer_var_offer_id.variableName].id),
                                                         param_id=input_vars_offer_id.parameterId)
        offer_node_var_map_client_id = variables_for_node(node_type="offer_mapping",
                                                          is_arr=False,
                                                          is_compl=False,
                                                          is_dict=False,
                                                          type_id=offer_var_client_id.primitiveTypeId,
                                                          node_variable=offer_var_client_id.variableName,
                                                          name=input_vars_client_id.parameterName,
                                                          outer_variable_id=str(
                                                              offer_vars_with_id[offer_var_client_id.variableName].id),
                                                          param_id=input_vars_client_id.parameterId)
        offer_node_var_map_client_id_type = variables_for_node(node_type="offer_mapping",
                                                               is_arr=False,
                                                               is_compl=False,
                                                               is_dict=False,
                                                               type_id=offer_var_client_id_type.primitiveTypeId,
                                                               node_variable=offer_var_client_id_type.variableName,
                                                               name=input_vars_client_id_type.parameterName,
                                                               outer_variable_id=str(offer_vars_with_id[
                                                                                         offer_var_client_id_type.variableName].id),
                                                               param_id=input_vars_client_id_type.parameterId)
        offer_node_var_map_control_group = variables_for_node(node_type="offer_mapping",
                                                              is_arr=False,
                                                              is_compl=False,
                                                              is_dict=False,
                                                              type_id=offer_var_control_group.primitiveTypeId,
                                                              node_variable=offer_var_control_group.variableName,
                                                              name=input_vars_control_group.parameterName,
                                                              outer_variable_id=str(offer_vars_with_id[
                                                                                        offer_var_control_group.variableName].id),
                                                              param_id=input_vars_control_group.parameterId)
        offer_node_var_map_score = variables_for_node(node_type="offer_mapping",
                                                      is_arr=False,
                                                      is_compl=False,
                                                      is_dict=False,
                                                      type_id=offer_var_score.primitiveTypeId,
                                                      node_variable=offer_var_score.variableName,
                                                      name=input_vars_score.parameterName,
                                                      outer_variable_id=str(
                                                          offer_vars_with_id[offer_var_score.variableName].id),
                                                      param_id=input_vars_score.parameterId)
        offer_node_var_map_start_at = variables_for_node(node_type="offer_mapping",
                                                         is_arr=False,
                                                         is_compl=False,
                                                         is_dict=False,
                                                         type_id=offer_var_start_at.primitiveTypeId,
                                                         node_variable=offer_var_start_at.variableName,
                                                         name=input_vars_start_at.parameterName,
                                                         outer_variable_id=str(
                                                             offer_vars_with_id[offer_var_start_at.variableName].id),
                                                         param_id=input_vars_start_at.parameterId)
        offer_node_var_map_end_at = variables_for_node(node_type="offer_mapping",
                                                       is_arr=False,
                                                       is_compl=False,
                                                       is_dict=False,
                                                       type_id=offer_var_end_at.primitiveTypeId,
                                                       node_variable=offer_var_end_at.variableName,
                                                       name=input_vars_end_at.parameterName,
                                                       outer_variable_id=str(
                                                           offer_vars_with_id[offer_var_end_at.variableName].id),
                                                       param_id=input_vars_end_at.parameterId)
        offer_output_var_mapping = variables_for_node(node_type="offer_output",
                                                      is_arr=True,
                                                      is_compl=True,
                                                      is_dict=False,
                                                      type_id=variable_for_offer.typeId,
                                                      node_variable=variable_for_offer.parameterName,
                                                      name=variable_for_offer.parameterName,
                                                      param_id=variable_for_offer.parameterId)
        offer_node_properties = offer_properties(offer_id=str(search_response.id),
                                                 offer_version_id=str(search_response.versionId),
                                                 offer_variables=[],
                                                 node_variables_mapping=[offer_node_var_map_product_code,
                                                                         offer_node_var_map_offer_id,
                                                                         offer_node_var_map_client_id,
                                                                         offer_node_var_map_client_id_type,
                                                                         offer_node_var_map_control_group,
                                                                         offer_node_var_map_score,
                                                                         offer_node_var_map_start_at,
                                                                         offer_node_var_map_end_at],
                                                 output_variable_mapping=offer_output_var_mapping)
        offer_update_body = offer_node_construct(x=700, y=202.22915649414062,
                                                 temp_version_id=temp_vers_id,
                                                 properties=offer_node_properties,
                                                 operation="update",
                                                 node_id=str(node_offer.nodeId))
        update_node(super_user, node_id=node_offer.nodeId, body=offer_update_body)
    with allure.step("Обновление узла отправка предложений в OS"):
        tech_service: ExternalServiceTechFullViewDto = ExternalServiceTechFullViewDto.construct(
            **get_tech_service(super_user, node_type="OFFER_STORAGE_WRITE").body[0])
        if continue_flg_marker is not None:
            continue_var = continue_flg_marker.args[0]
        else:
            continue_var = False
        node_os_up_data = os_write_construct(diagram_vers_id=diagram_constructor["temp_version_id"],
                                             output_var_name=variable_for_offer.parameterName,
                                             output_var_type_id=variable_for_offer.typeId,
                                             service_id=tech_service.serviceId,
                                             service_version_id=tech_service.versionId,
                                             continue_flg=continue_var)
        update_node(super_user, node_id=node_os_write.nodeId, body=node_os_up_data)
    with allure.step("Обновление узла завершение"):
        node_finish_info: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_finish.nodeId).body)
        finish_up_body = NodeUpdateDto.construct(nodeTypeId=node_finish_info.nodeTypeId,
                                                 diagramVersionId=temp_vers_id,
                                                 nodeName=node_finish_info.nodeName,
                                                 nodeDescription=node_finish_info.nodeDescription,
                                                 properties=node_finish_info.properties,
                                                 metaInfo=node_finish_info.metaInfo, validFlag=True)
        update_node(super_user, node_id=node_finish.nodeId, body=finish_up_body)

    new_diagram_name = "ag_test_diagram_os_read" + generate_string()
    diagram_description = "diagram created in test"
    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_vers_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]
    save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, saved_version_id).body)

    return {"diagram_name": new_diagram_name, "diagram_data": save_data}
