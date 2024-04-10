import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import OfferFullViewDto, ScriptFullView, ComplexTypeGetFullView, \
    DiagramInOutParameterFullViewDto, ResponseDto, NodeViewWithVariablesDto, DiagramViewDto, \
    NodeViewShortInfo, NodeValidateDto
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import update_node, get_node_by_id, create_node, \
    delete_node_by_id
from products.Decision.utilities.custom_models import VariableParams, IntNodeType
from products.Decision.utilities.node_cunstructors import variables_for_node, offer_variable, offer_properties, \
    offer_node_construct


@allure.epic("Диаграммы")
@allure.feature("Узел предложения")
class TestDiagramsOfferNode:
    @allure.story(
        "Нет ошибок, если узел корректно заполнен"
    )
    @allure.title(
        "Обновить узел предложения добавив к нему валидное предложение"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_cmplx", varType="out", isComplex=True, isArray=True,
                                               isConst=False, varValue="offer_complex_type")])
    @pytest.mark.nodes(["предложение"])
    @pytest.mark.smoke
    def test_create_diagram_with_offer(self, super_user, diagram_constructor):
        node_offer: NodeViewShortInfo = diagram_constructor["nodes"]["предложение"]
        diagram_param_in: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
        diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_cmplx"]
        temp_version_id = diagram_constructor["temp_version_id"]
        complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]

        offer: OfferFullViewDto = diagram_constructor["offer"]
        with allure.step("Обновление узла предложения"):
            node_var_mapping = variables_for_node(node_type="offer_mapping",
                                                  is_arr=False,
                                                  is_compl=False,
                                                  is_dict=False,
                                                  type_id="1",
                                                  node_variable=offer.offerVariables[0]["variableName"],
                                                  name=diagram_param_in.parameterName,
                                                  outer_variable_id=offer.offerVariables[0]["id"],
                                                  param_id=diagram_param_in.parameterId)
            output_var_mapping = variables_for_node(node_type="offer_output",
                                                    is_arr=True,
                                                    is_compl=True,
                                                    is_dict=False,
                                                    type_id=complex_type.versionId,
                                                    node_variable=diagram_param_out.parameterName,
                                                    name=diagram_param_out.parameterName,
                                                    param_id=diagram_param_out.parameterId)
            node_offer_properties = offer_properties(offer_id=offer.id,
                                                     offer_version_id=offer.versionId,
                                                     offer_variables=[],
                                                     node_variables_mapping=[node_var_mapping],
                                                     output_variable_mapping=output_var_mapping)
            update_body = offer_node_construct(x=700, y=202.22915649414062,
                                               node_id=str(node_offer.nodeId),
                                               temp_version_id=temp_version_id,
                                               properties=node_offer_properties,
                                               operation="update")
            update_node(super_user, node_id=node_offer.nodeId, body=update_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=update_body.nodeTypeId,
                            properties=update_body.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_offer.nodeId).body
            )
            assert node_view.properties["versionId"] == str(offer.versionId) and \
                   node_view.properties["outputVariableMapping"]["typeId"] == str(complex_type.versionId) and \
                   node_view.validFlag

    @allure.story("Узел предложения создаётся")
    @allure.title(
        "Создать диаграмму с узлом предложения без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-3379")
    @pytest.mark.smoke
    def test_create_node_offer(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла узла предложения"):
            node_offer = offer_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_offer_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_offer).body
            )
            node_offer_id = node_offer_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step(
                "Проверка, что идентификатор узла рассчёта корректен и равен 19-предложение"
        ):
            assert diagram.nodes[str(node_offer_id)].nodeTypeId == 19

    @allure.story("Узел предложения удаляется")
    @allure.title(
        "Создать диаграмму с узлом предложения без параметров, удалить, увидеть, что удалён"
    )
    @pytest.mark.scenario("DEV-3379")
    @pytest.mark.smoke
    def test_delete_node_offer(self, super_user, create_temp_diagram):
        with allure.step("Создание template диаграммы"):
            template = create_temp_diagram
        with allure.step("Создание узла предложения"):
            node_offer = offer_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_offer_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_offer).body
            )
            node_offer_id = node_offer_response.uuid
        with allure.step("Удаление узла по id"):
            delete_node_by_id(super_user, node_offer_id)
        with allure.step("Проверка, что узел не найден"):
            with pytest.raises(HTTPError):
                assert get_node_by_id(super_user, node_offer_id).status == 404
