import time

import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import ResponseDto, DiagramInOutParameterFullViewDto, AggregateGetFullView, \
    RetentionType, RetentionTimeUnit, DeployConfigurationFullDto, NodeViewWithVariablesDto, \
    NodeValidateDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, deploy_config
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id
from products.Decision.utilities.node_cunstructors import aggregate_properties, aggregate_compute_out_var, \
    grouping_element_map, aggregate_compute_properties, aggregate_compute_node_construct, node_update_construct


@allure.epic("Рассчёт агрегата")
@allure.feature("Рассчёт агрегата")
class TestRuntimeAggrCompute:
    @allure.story(
        "Диаграмма с узлом рассчёта агрегата отправляется на развёртку"
    )
    @allure.title(
        "Отправить диаграмму с узлом рассчёта агрегата на развёртование, проверить, что появилась в списке деплоев"
    )
    @allure.issue("DEV-12500")
    def test_submit_diagram_with_aggregate_compute(self, super_user,
                                                   diagram_aggregate_calculation,
                                                   save_diagrams_gen):
        node_aggr_comp: ResponseDto = diagram_aggregate_calculation["node_aggr_compute"]
        in_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["in_param"]
        in_aggr_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["in_aggr_param"]
        out_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["out_param"]
        node_end = diagram_aggregate_calculation["node_end"]
        finish_variable = diagram_aggregate_calculation["finish_var"]
        node_start = diagram_aggregate_calculation["node_start"]
        # diagram_version_id = diagram_offer["create_result"].uuid
        temp_version_id = diagram_aggregate_calculation["template"]["versionId"]
        diagram_id = diagram_aggregate_calculation["template"]["diagramId"]
        aggregate: AggregateGetFullView = diagram_aggregate_calculation["aggregate"]
        grouping_element = diagram_aggregate_calculation["grouping_element"]
        aggregate_function = diagram_aggregate_calculation["aggregate_function"]
        with allure.step("Обновление узла предложения"):
            aggr_for_node = aggregate_properties(aggregate_id=aggregate.aggregateId,
                                                 aggregate_version_id=aggregate.versionId,
                                                 diagram_aggregate_element=in_param.parameterName,
                                                 is_used_in_diagram=True,
                                                 aggregate_element_type_id="1",
                                                 aggregate_function=aggregate_function)
            output_var_mapping = aggregate_compute_out_var(is_arr=False,
                                                           is_compl=False,
                                                           aggregate=aggr_for_node,
                                                           is_dict=False,
                                                           var_name=out_param.parameterName,
                                                           type_id="1")
            gr_element = grouping_element_map(aggregate_element=grouping_element,
                                              diagram_element=in_aggr_param.parameterName,
                                              full_path_value=grouping_element,
                                              simple_name_value=grouping_element,
                                              column=grouping_element)
            node_aggr_properties = aggregate_compute_properties(output_vars=[output_var_mapping],
                                                                retention_type=RetentionType.process,
                                                                retention_time_value=28,
                                                                retention_time_unit=RetentionTimeUnit.d,
                                                                grouping_elements=[gr_element])
            update_body = aggregate_compute_node_construct(x=700, y=202.22915649414062,
                                                           temp_version_id=temp_version_id,
                                                           properties=node_aggr_properties,
                                                           operation="update")
            update_node(super_user, node_id=node_aggr_comp.uuid, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
            finish_up_body = node_update_construct(x=1400, y=202,
                                                   temp_version_id=temp_version_id,
                                                   node_type="finish",
                                                   variables=[finish_variable])
            update_node(super_user, node_id=node_end.uuid, body=finish_up_body)
        finish_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_end.uuid).body)
        start_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_start.uuid).body)
        with allure.step("Сохранение диаграммы"):
            diagram_name = "ag_diagram_aggregate_comp" + "_" + generate_string()
            diagram_description = 'diagram created in test'
            response_save: ResponseDto = save_diagrams_gen.save_diagram(diagram_id=diagram_id,
                                                                        temp_version_id=temp_version_id,
                                                                        new_diagram_name=diagram_name,
                                                                        diagram_description=diagram_description)
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
            # submit_response = put_diagram_submit(super_user, version_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлом рассчёта агрегата разворачивается"
    )
    @allure.title(
        "Развернуть диаграмму с узлом рассчёта агрегата, проверить, что развернулась"
    )
    @pytest.mark.skip("DEV-12500")
    def test_deploy_diagram_aggr_compute(self, super_user,
                                         diagram_aggr_comp_submit,
                                         deploy_diagrams_gen):
        env_id = diagram_aggr_comp_submit["env_id"]
        deploy_id = diagram_aggr_comp_submit["deploy_id"]
        diagram_id = diagram_aggr_comp_submit["diagram_id"]
        diagram_name = diagram_aggr_comp_submit["diagram_name"]
        with allure.step("Деплой подготовленной диаграммы"):
            deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            deployed = check_deploy_status(user=super_user,
                                           diagram_name=diagram_name,
                                           diagram_id=diagram_id,
                                           status="DEPLOYED")
            assert deployed

    @allure.story(
        "В диаграмму с узлом рассчёта агрегата возможно отправить сообщение"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом рассчёта агрегата, получить ответ"
    )
    @pytest.mark.skip("DEV-12500")
    def test_send_message_diagram_with_aggr_comp_node(self, super_user,
                                                      diagram_aggr_comp_submit,
                                                      deploy_diagrams_gen,
                                                      integration_user):
        env_id = diagram_aggr_comp_submit["env_id"]
        deploy_id = diagram_aggr_comp_submit["deploy_id"]
        diagram_id = diagram_aggr_comp_submit["diagram_id"]
        diagram_name = diagram_aggr_comp_submit["diagram_name"]
        in_param: DiagramInOutParameterFullViewDto = diagram_aggr_comp_submit["in_param"]
        in_aggr_param: DiagramInOutParameterFullViewDto = diagram_aggr_comp_submit["in_aggr_param"]
        out_param: DiagramInOutParameterFullViewDto = diagram_aggr_comp_submit["out_param"]
        with allure.step("Деплой подготовленной диаграммы"):
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            deployed = check_deploy_status(user=super_user,
                                           diagram_name=diagram_name,
                                           diagram_id=diagram_id,
                                           status="DEPLOYED")
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            message_response = send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{in_param.parameterName}": 1,
                      f"{in_aggr_param.parameterName}": 1}
            ).body
        with allure.step("Сообщение пришло и статус исполнения диаграммы 1 - без ошибки"):
            assert message_response[f"{out_param.parameterName}"] is not None and \
                   message_response["diagram_execute_status"] == "1"
