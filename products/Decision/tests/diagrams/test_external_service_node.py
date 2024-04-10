import uuid

import glamor as allure
import pytest

from products.Decision.framework.model import (
    ResponseDto,
    DiagramViewDto,
    NodeViewShortInfo,
    DiagramInOutParametersViewDto,
    DiagramInOutParameterFullViewDto,
    ExternalServiceFullViewDto,
    NodeViewWithVariablesDto, ExternalService,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version,
)
from products.Decision.framework.steps.decision_steps_nodes import (
    create_node,
    update_node,
    get_node_by_id, remap_external_service_node,
)
from products.Decision.utilities.node_cunstructors import (
    external_service_node_construct,
)


@allure.epic("Диаграммы")
@allure.feature("Блок вызова внешнего сервиса")
class TestDiagramsExternalServiceNode:
    @allure.story("Возможно создать узел ВВС")
    @allure.title("Создать диаграмму с узлом ВВС без параметров, увидеть, что создался")
    @pytest.mark.scenario("DEV-15464")
    @pytest.mark.smoke
    def test_create_node_ext_serv_empty(self, super_user, create_temp_diagram):
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
        with allure.step("Создание узла внешнего сервиса"):
            node_ext_serv = external_service_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_ext_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_ext_serv).body
            )
            node_ext_id = node_ext_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step("Проверка, что создался нужный узел"):
            assert diagram.nodes[str(node_ext_id)].nodeTypeId == 8

    @allure.story(
        "При корректном заполнении узла валидация не обнаруживает ошибок"
    )
    @allure.title(
        "В узел внешнего сервиса добавить внешний сервис проверить validFlag"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.smoke
    def test_add_service_to_serv_node(self, super_user, diagram_external_service):
        template: DiagramInOutParametersViewDto = diagram_external_service["diagram_template"]
        node_ext_id = diagram_external_service["node_ext_id"]
        diagram_variable: DiagramInOutParameterFullViewDto = diagram_external_service["diagram_variable"]
        external_service: ExternalServiceFullViewDto = diagram_external_service["external_service"]
        service_version_id = external_service.versionId
        service_id = external_service.serviceId
        mapping_properties: ExternalService = remap_external_service_node(super_user, node_id=node_ext_id,
                                                                          service_id=service_id,
                                                                          service_version_id=service_version_id)
        for var in mapping_properties.outputVariablesMapping:
            if var.nodeVariable != "externalServiceStatusCode":
                var.variableName = diagram_variable.parameterName
                var.id = diagram_variable.parameterId

        mapping_properties.inputVariablesMapping[0].variableName = diagram_variable.parameterName
        mapping_properties.inputVariablesMapping[0].id = diagram_variable.parameterId
        node_up = external_service_node_construct(
            x=700,
            y=202.22915649414062,
            temp_version_id=template.versionId,
            properties=mapping_properties,
            operation="update",
        )
        update_node(super_user, node_id=node_ext_id, body=node_up)
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_ext_id).body
            )
        assert node_view.validFlag

    @allure.story(
        "serviceId - при указании на несуществующий serciveId - узел невалидный"
    )
    @allure.issue("DEV-6496")
    @allure.title(
        "В узел внешнего сервиса добавить внешний сервис, несуществующий параметр serviceId"
    )
    @pytest.mark.scenario("DEV-6398")
    def test_add_non_existent_service_id_to_serv_node(
            self, super_user, diagram_external_service
    ):
        wrong_service_id = str(uuid.uuid4())
        wrong_service_version_id = str(uuid.uuid4())

        template: DiagramInOutParametersViewDto = diagram_external_service["diagram_template"]
        node_ext_id = diagram_external_service["node_ext_id"]
        diagram_variable: DiagramInOutParameterFullViewDto = diagram_external_service["diagram_variable"]
        external_service: ExternalServiceFullViewDto = diagram_external_service["external_service"]
        service_version_id = external_service.versionId
        service_id = external_service.serviceId
        mapping_properties: ExternalService = remap_external_service_node(super_user, node_id=node_ext_id,
                                                                          service_id=service_id,
                                                                          service_version_id=service_version_id)
        for var in mapping_properties.outputVariablesMapping:
            if var.nodeVariable != "externalServiceStatusCode":
                var.variableName = diagram_variable.parameterName
                var.id = diagram_variable.parameterId
        mapping_properties.inputVariablesMapping[0].variableName = diagram_variable.parameterName
        mapping_properties.inputVariablesMapping[0].id = diagram_variable.parameterId
        mapping_properties.serviceId = wrong_service_id
        mapping_properties.versionId = wrong_service_version_id
        node_up = external_service_node_construct(
            x=700,
            y=202.22915649414062,
            temp_version_id=template.versionId,
            properties=mapping_properties,
            operation="update",
        )
        update_node(super_user, node_id=node_ext_id, body=node_up)
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_ext_id).body
            )
        assert not node_view.validFlag

    @allure.story(
        "Перечень атрибутов inputVariablesMapping при несоответствии актуальному перечню соответствующих "
        "входных атрибутов ВСа, на который ссылается узел и соответствующих переменных диаграммы, "
        "узел невалидный"
    )
    @allure.title(
        "В узел внешнего сервиса добавить внешний сервис с невалидным маппингом входных атрибутов"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-6496")
    @pytest.mark.parametrize(
        "bad_param", ["wrong_diagram_var"]
    )
    def test_add_wrong_input_var_mapping_to_serv_node(
            self, super_user, diagram_external_service, bad_param
    ):
        template: DiagramInOutParametersViewDto = diagram_external_service["diagram_template"]
        node_ext_id = diagram_external_service["node_ext_id"]
        diagram_variable: DiagramInOutParameterFullViewDto = diagram_external_service["diagram_variable"]
        external_service: ExternalServiceFullViewDto = diagram_external_service["external_service"]
        service_version_id = external_service.versionId
        service_id = external_service.serviceId
        mapping_properties: ExternalService = remap_external_service_node(super_user, node_id=node_ext_id,
                                                                          service_id=service_id,
                                                                          service_version_id=service_version_id)
        for var in mapping_properties.outputVariablesMapping:
            if var.nodeVariable != "externalServiceStatusCode":
                var.variableName = diagram_variable.parameterName
                var.id = diagram_variable.parameterId
        if bad_param == "wrong_diagram_var":
            mapping_properties.inputVariablesMapping[0].variableName = "wrong_diagram_var_name"
            mapping_properties.inputVariablesMapping[0].id = str(uuid.uuid4())
        node_up = external_service_node_construct(
            x=700,
            y=202.22915649414062,
            temp_version_id=template.versionId,
            properties=mapping_properties,
            operation="update",
        )
        update_node(super_user, node_id=node_ext_id, body=node_up)

        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_ext_id).body
            )
        assert not node_view.validFlag and node_view.validationPayload["nodeValidationMap"]["inputVariablesMapping"] \
            [f"{mapping_properties.inputVariablesMapping[0].rowKey}"] \
            ["variableName"] == "Переменная не найдена или не была рассчитана"

    @allure.story(
        "Перечень атрибутов outputVariablesMapping при несоответствии актуальному перечню соответствующих "
        "выходных атрибутов ВСа, на который ссылается узел; узел невалидный"
    )
    @allure.title(
        "В узел внешнего сервиса добавить внешний сервис с невалидным маппингом выходных атрибутов"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-6496")
    @pytest.mark.parametrize(
        "bad_param", ["wrong_diagram_var"]
    )
    def test_add_wrong_output_var_mapping_to_serv_node(
            self, super_user, diagram_external_service, bad_param
    ):
        template: DiagramInOutParametersViewDto = diagram_external_service["diagram_template"]
        node_ext_id = diagram_external_service["node_ext_id"]
        diagram_variable: DiagramInOutParameterFullViewDto = diagram_external_service["diagram_variable"]
        external_service: ExternalServiceFullViewDto = diagram_external_service["external_service"]
        service_version_id = external_service.versionId
        service_id = external_service.serviceId
        mapping_properties: ExternalService = remap_external_service_node(super_user, node_id=node_ext_id,
                                                                          service_id=service_id,
                                                                          service_version_id=service_version_id)
        out_var_row_key = None
        for var in mapping_properties.outputVariablesMapping:
            if var.nodeVariable != "externalServiceStatusCode":
                if bad_param == "wrong_diagram_var":
                    var.variableName = "wrong_diagram_var_name"
                    var.id = str(uuid.uuid4())
                out_var_row_key = var.rowKey
        mapping_properties.inputVariablesMapping[0].variableName = diagram_variable.parameterName
        mapping_properties.inputVariablesMapping[0].id = diagram_variable.parameterId
        node_up = external_service_node_construct(
            x=700,
            y=202.22915649414062,
            temp_version_id=template.versionId,
            properties=mapping_properties,
            operation="update",
        )
        update_node(super_user, node_id=node_ext_id, body=node_up)
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_ext_id).body
            )
        assert not node_view.validFlag and node_view.validationPayload["nodeValidationMap"]["outputVariablesMapping"] \
            [f"{out_var_row_key}"]["variableName"] == "Переменная не найдена или не была рассчитана"
