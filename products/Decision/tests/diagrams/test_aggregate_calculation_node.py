import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import DiagramInOutParameterFullViewDto, ResponseDto, AggregateGetFullView, \
    RetentionTimeUnit, RetentionType, NodeViewWithVariablesDto, DiagramViewDto, NodeViewShortInfo, NodeValidateDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id, create_node, \
    delete_node_by_id
from products.Decision.utilities.node_cunstructors import aggregate_properties, aggregate_compute_out_var, \
    grouping_element_map, aggregate_compute_properties, aggregate_compute_node_construct


@allure.epic("Диаграммы")
@allure.feature("Узел расчёт агрегата")
class TestDiagramsAggrCalcNode:
    @allure.story(
        "Нет ошибок валидации, если узел корректно заполнен"
    )
    @allure.title(
        "Обновить узел расчёта агрегата добавив к нему валидный агрегат"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.smoke
    def test_create_diagram_with_aggregate_node(self, super_user,
                                                diagram_aggregate_calculation,
                                                save_diagrams_gen):
        node_aggr_comp: ResponseDto = diagram_aggregate_calculation["node_aggr_compute"]
        in_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["in_param"]
        in_aggr_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["in_aggr_param"]
        out_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["out_param"]
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
                                                           type_id="1",
                                                           param_id=out_param.parameterId)
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
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_aggr_comp.uuid).body
            )
        # with allure.step("Сохранение диаграммы"):
        #     new_diagram_name = "ag_diagram_aggr_compute" + "_" + generate_diagram_name_description(8, 1)["rand_name"]
        #     diagram_description = 'diagram created in test'
        #     response_save: ResponseDto = save_diagrams_gen.save_diagram(diagram_id=diagram_id,
        #                                                                 temp_version_id=temp_version_id,
        #                                                                 new_diagram_name=new_diagram_name,
        #                                                                 diagram_description=diagram_description)
        assert node_view.validFlag and \
               node_view.properties["groupingElements"][0]["aggregateElement"] == grouping_element and \
               node_view.properties["outputVariablesMapping"][0]["aggregate"]["versionId"] == aggregate.versionId

    @allure.story("Узел расчёта агрегата создаётся")
    @allure.title(
        "Создать диаграмму с узлом расчёта агрегата без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15459")
    @pytest.mark.smoke
    def test_create_node_aggr_comp(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла предложения"):
            node_aggr_comp = aggregate_compute_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_aggr_comp_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_aggr_comp).body
            )
            node_aggr_comp_id = node_aggr_comp_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла рассчёта корректен и равен 11-предложение"
        ):
            assert diagram.nodes[str(node_aggr_comp_id)].nodeTypeId == 11

    @allure.story("Узел расчёта агрегата удаляется")
    @allure.title(
        "Создать диаграмму с узлом расчёта агрегата без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.scenario("DEV-15459")
    @pytest.mark.smoke
    def test_delete_node_aggr_comp(self, super_user, create_temp_diagram):
        template = create_temp_diagram
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        with allure.step("Создание узла узла предложения"):
            node_aggr_comp = aggregate_compute_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_aggr_comp_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_aggr_comp).body
            )
            node_aggr_comp_id = node_aggr_comp_response.uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_aggr_comp_id)
        with allure.step("Проверка, что поиск узла возвращается со статусом 404"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_aggr_comp_id).status == 404
