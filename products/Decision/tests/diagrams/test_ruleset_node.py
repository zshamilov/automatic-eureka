import uuid

import glamor as allure
import pytest

from products.Decision.framework.model import (
    ResponseDto,
    DiagramViewDto,
    NodeViewShortInfo,
    NodeViewWithVariablesDto,
    RuleTypeGetFullView,
    RuleTypeCreateDto,
    RuleTypeUpdateDto,
    DiagramInOutParameterFullViewDto,
    AttributeCreate, NodeValidateDto,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version,
)
from products.Decision.framework.steps.decision_steps_nodes import (
    create_node,
    update_node,
    get_node_by_id,
)
from products.Decision.framework.steps.decision_steps_rule_types_api import (
    ruletype_list,
    create_ruletype,
    delete_ruletype_by_id,
    get_ruletype_by_id,
    update_ruletype,
)
from products.Decision.tests.diagrams.test_add_diagrams import (
    generate_diagram_name_description,
)
from products.Decision.utilities.node_cunstructors import (
    ruleset_node_construct,
    rule_set_properties,
    rule_set_var_const,
)


@allure.epic("Диаграммы")
@allure.feature("Узел набор правил")
class TestDiagramsRulesetNode:
    @allure.story("Узел можно создать с NodeType = 7")
    @allure.title(
        "Создать диаграмму с узлом набора правил без параметров, увидеть, что создался"
    )
    @pytest.mark.scenario("DEV-15458")
    @pytest.mark.smoke
    def test_create_node_ruleset_empty(self, super_user, create_temp_diagram):
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла набора правил"):
            node_rule = ruleset_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_rule_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_rule).body
            )
            node_rule_id = node_rule_response.uuid
        with allure.step("Получение информации о диаграмме"):
            diagram = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, temp_version_id).body
            )
            for key, value in diagram.nodes.items():
                diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        with allure.step("Проверка, что создался нужный узел"):
            assert diagram.nodes[str(node_rule_id)].nodeTypeId == 7

    @allure.story(
        "Для параметра ruleVariable поле typeId может быть только идентификатором комплексного типа Rule"
    )
    @allure.title(
        "Поместить в rule variable валидный и невалидный идентификаторы, проверить валидацию узла"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("valid_var", [True, False])
    @pytest.mark.smoke
    def test_rule_variable(self, super_user, create_temp_diagram, valid_var):
        var_id = None
        if valid_var:
            var_id = "4d16435a-7bdb-4b0b-96cb-3d40ccac3260"
        else:
            var_id = str(uuid.uuid4())
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла набора правил"):
            node_rule = ruleset_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_rule_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_rule).body
            )
            node_rule_id = node_rule_response.uuid
            rule_id = None
            rules = []
            for rule in ruletype_list(super_user).body.values():
                rules.append(RuleTypeGetFullView.construct(**rule))
            for rule in rules:
                if rule.typeName == "Decline":
                    rule_id = rule.typeId
        with allure.step(
            "Обновление узла рассчёта на различные переменные узла правил"
        ):
            rule_var = rule_set_var_const(
                is_arr=True,
                is_complex=True,
                var_name="rule_var",
                type_id=var_id,
                var_path=None,
                var_root_id=None,
            )
            rule_properties = rule_set_properties(
                apply_rule=True,
                rule_name="test_rule",
                rule_code="test",
                rule_type_id=rule_id,
                rule_description="made in test",
                rule_expression="1<2",
                rule_weight_factor=1.0,
            )
            node_rule_upd = ruleset_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=template["versionId"],
                rule_variable=rule_var,
                rules=[rule_properties],
                operation="update",
            )
            update_node(super_user, node_id=node_rule_id, body=node_rule_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_rule_upd.nodeTypeId,
                            properties=node_rule_upd.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_rule_id).body
            )
        with allure.step("Проверка, что переменная узла корректна"):
            assert (
                node_view.properties["ruleVariable"]["typeId"]
                == "4d16435a-7bdb-4b0b-96cb-3d40ccac3260"
            )

    @allure.story(
        "Результатом расчета выражения в ruleExpression является логическое выражение"
    )
    @allure.title(
        "Поместить в expression логическое и не логическое выражение, проверить валидацию узла"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("expr, valid", [("1<2", True), ("hello world", False)])
    @pytest.mark.smoke
    @pytest.mark.skip("устарел после смены подхода валидации экспрешн эдитора")
    def test_rule_expression_vars(
        self, super_user, create_temp_diagram, valid, expr
    ):
        var_id = "4d16435a-7bdb-4b0b-96cb-3d40ccac3260"
        with allure.step("Создание шаблона диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
            diagram_id = template["diagramId"]
        with allure.step("Создание узла набора правил"):
            node_rule = ruleset_node_construct(
                x=700, y=202.22915649414062, temp_version_id=template["versionId"]
            )
            node_rule_response: ResponseDto = ResponseDto.construct(
                **create_node(super_user, node_rule).body
            )
            node_rule_id = node_rule_response.uuid
            rule_id = None
            rules = []
            for rule in ruletype_list(super_user).body.values():
                rules.append(RuleTypeGetFullView.construct(**rule))
            for rule in rules:
                if rule.typeName == "Decline":
                    rule_id = rule.typeId
        with allure.step(
            "Обновление узла рассчёта на различные переменные узла правил"
        ):
            rule_var = rule_set_var_const(
                is_arr=True,
                is_complex=True,
                var_name="rule_var",
                type_id=var_id,
                var_path=None,
                var_root_id=None,
            )
            rule_properties = rule_set_properties(
                apply_rule=True,
                rule_name="test_rule",
                rule_code="test",
                rule_type_id=rule_id,
                rule_description="made in test",
                rule_expression=expr,
                rule_weight_factor=1.0,
            )
            node_rule_upd = ruleset_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=template["versionId"],
                rule_variable=rule_var,
                rules=[rule_properties],
                operation="update",
            )
            update_node(super_user, node_id=node_rule_id, body=node_rule_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_rule_upd.nodeTypeId,
                            properties=node_rule_upd.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_rule_id).body
            )
        with allure.step("Проверка, что переменная узла корректна"):
            assert node_view.validFlag == valid

    @allure.story("Возможно получить список правил")
    @allure.title(
        "Запросить список правил, проверить, что возвращается нужна информация"
    )
    @pytest.mark.scenario("DEV-15458")
    @pytest.mark.smoke
    def test_rule_list(self, super_user):
        rules = []
        with allure.step("Получение списка правил"):
            for rule in ruletype_list(super_user).body.values():
                rules.append(RuleTypeGetFullView.construct(**rule))
        with allure.step(
            "Проверка, что у всех объектов списка присутствует нужная информация"
        ):
            rules_contain_req_fields = next(
                (
                    rule
                    for rule in rules
                    if rule.typeName is not None
                    and rule.typeId is not None
                    and rule.changeDt is not None
                    and rule.createDt is not None
                    and rule.displayName is not None
                ),
                True,
            )
            assert rules_contain_req_fields

    @allure.story("Можно удалить тип правила")
    @allure.title("Удалить правило, проверить, что пропало из списка")
    @pytest.mark.scenario("DEV-15458")
    @pytest.mark.smoke
    def test_rule_delete(self, super_user):
        rule_found = False
        with allure.step("Создание правила"):
            create_response: ResponseDto = ResponseDto.construct(
                **create_ruletype(
                    super_user,
                    body=RuleTypeCreateDto(typeName="Compare", displayName="Compare"),
                ).body
            )
        with allure.step("Удаление правила"):
            delete_ruletype_by_id(super_user, create_response.uuid)
        with allure.step("Получение списка правил"):
            rules = []
            for rule in ruletype_list(super_user).body.values():
                rules.append(RuleTypeGetFullView.construct(**rule))
            for rule in rules:
                if rule.typeId == create_response.uuid:
                    rule_found = True
        with allure.step("Проверка, что правило не найдено"):
            assert not rule_found

    @allure.story("Можно добавить тип правила")
    @allure.title("Создать правило, проверить, что появляется в списке правил")
    @pytest.mark.scenario("DEV-15458")
    @pytest.mark.smoke
    def test_rule_create(self, super_user, create_rule_gen):
        rule_found = False
        rule_name = "rule_" + generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Создание правила"):
            create_response: ResponseDto = create_rule_gen.create_rule(
                type_name=rule_name, display_name=rule_name
            )
        with allure.step("Получение списка правил"):
            rules = []
            for rule in ruletype_list(super_user).body.values():
                rules.append(RuleTypeGetFullView.construct(**rule))
            for rule in rules:
                if rule.typeId == create_response.uuid:
                    rule_found = True
        with allure.step("Проверка, что правило найдено"):
            assert rule_found

    @allure.story("Можно получить конкретное правило")
    @allure.title("Найти правило по идентификатору, проверить корректность информации")
    @pytest.mark.scenario("DEV-15458")
    @pytest.mark.smoke
    def test_rule_search(self, super_user, create_rule_gen):
        rule_name = "rule_" + generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Создание правила"):
            create_response: ResponseDto = create_rule_gen.create_rule(
                type_name=rule_name, display_name=rule_name
            )
        with allure.step("Получение информации о правиле"):
            rule: RuleTypeGetFullView = RuleTypeGetFullView.construct(
                **get_ruletype_by_id(super_user, create_response.uuid).body
            )
        with allure.step(
            "Проверка, что в информации о правиле содержится информация, заданная при создании"
        ):
            assert (
                rule.typeId == create_response.uuid
                and rule.typeName == rule_name
                and rule.displayName == rule_name
                and rule.createDt is not None
                and rule.changeDt is not None
                and rule.createByUser is not None
                and rule.lastChangeByUser is not None
            )

    @allure.story("Можно отредактировать правило")
    @allure.title("Обновить правило, проверить, что обновилось")
    @pytest.mark.scenario("DEV-15458")
    @pytest.mark.smoke
    def test_rule_update(self, super_user, create_rule_gen):
        rule_name = "rule_" + generate_diagram_name_description(8, 1)["rand_name"]
        rule_name_up = (
            "rule_updated_" + generate_diagram_name_description(8, 1)["rand_name"]
        )
        with allure.step("Создание правила"):
            create_response: ResponseDto = create_rule_gen.create_rule(
                type_name=rule_name, display_name=rule_name
            )
        with allure.step("Обновление правила"):
            update_ruletype(
                super_user,
                create_response.uuid,
                body=RuleTypeUpdateDto(typeName=rule_name_up, displayName=rule_name_up),
            )
        with allure.step("Получение информации о правиле"):
            rule: RuleTypeGetFullView = RuleTypeGetFullView.construct(
                **get_ruletype_by_id(super_user, create_response.uuid).body
            )
        with allure.step("Проверка, что правило обновлено"):
            assert (
                rule.typeId == create_response.uuid
                and rule.typeName == rule_name_up
                and rule.displayName == rule_name_up
            )

    @allure.story(
        "ruleObject ссылается на существующий элемент данных диаграммы или пуст. если комплексный тип в "
        "поле ruleObject отсутствует в списке inputVaribles блока - ValidFlag = false"
    )
    @allure.issue("DEV-6496")
    @allure.title(
        "Подать в variable path переменной правила существующий и несуществующий элемент данных диаграммы"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.parametrize("valid_path, valid", [(True, True), (False, False)])
    def test_rule_object(self, super_user, diagram_ruleset, valid_path, valid):
        var_id = "4d16435a-7bdb-4b0b-96cb-3d40ccac3260"
        var_path = None
        with allure.step(
            "Создание диаграммы с комплексной переменной, узлами: начало, набор правил, завершение"
        ):
            node_rule_id = diagram_ruleset["node_rule_id"]
            diagram_variable: DiagramInOutParameterFullViewDto = diagram_ruleset[
                "diagram_variable"
            ]
            template = diagram_ruleset["diagram_template"]
            if valid_path:
                var_path = f"{diagram_variable.parameterName}"
            else:
                var_path = "he-he i am not a path"
        with allure.step("Поиск идентификатора правила"):
            rule_id = None
            rules = []
            for rule in ruletype_list(super_user).body.values():
                rules.append(RuleTypeGetFullView.construct(**rule))
            for rule in rules:
                if rule.typeName == "Decline":
                    rule_id = rule.typeId
        with allure.step("Обновление узла рассчёта с указанием rule object"):
            rule_var = rule_set_var_const(
                is_arr=True,
                is_complex=True,
                var_name="rule_var",
                type_id=var_id,
                var_path=var_path,
                var_root_id=None,
            )
            rule_properties = rule_set_properties(
                apply_rule=True,
                rule_name="test_rule",
                rule_code="test",
                rule_type_id=rule_id,
                rule_description="made in test",
                rule_expression="1<2",
                rule_weight_factor=1.0,
            )
            node_rule_upd = ruleset_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=template.versionId,
                rule_variable=rule_var,
                rules=[rule_properties],
                operation="update",
            )
            update_node(super_user, node_id=node_rule_id, body=node_rule_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_rule_upd.nodeTypeId,
                            properties=node_rule_upd.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_rule_id).body
            )
        with allure.step("Проверка валидации узла"):
            assert node_view.validFlag == valid

    @allure.story(
        "ruleExpression содержит ссылки только на существующие элементы данных диаграммы, если в выражении "
        "присутствует переменная, которой нет в inputVariables узла или в составе комплексного типа из "
        "inputVariables - validFlag = false"
    )
    @allure.title(
        "Подать в ruleExpression ссылку на существующий и несуществующий элемент диаграммы "
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-6496")
    @pytest.mark.parametrize("valid_expr_path, valid", [(True, True), (False, False)])
    def test_rule_expression_ctype(self, super_user, diagram_ruleset, valid_expr_path, valid):
        var_id = "4d16435a-7bdb-4b0b-96cb-3d40ccac3260"
        expr = None
        with allure.step("Создание шаблона диаграммы"):
            node_rule_id = diagram_ruleset["node_rule_id"]
            diagram_variable: DiagramInOutParameterFullViewDto = diagram_ruleset[
                "diagram_variable"
            ]
            ctype_attr: AttributeCreate = diagram_ruleset["ctype_attr"]
            template = diagram_ruleset["diagram_template"]
            if valid_expr_path:
                expr = (
                    f"${diagram_variable.parameterName}"
                    + "."
                    + f"{ctype_attr.attributeName} > 1"
                )
            else:
                expr = "$not_a_var > 1"
        with allure.step("Поиск идентификатора правила"):
            rule_id = None
            rules = []
            for rule in ruletype_list(super_user).body.values():
                rules.append(RuleTypeGetFullView.construct(**rule))
            for rule in rules:
                if rule.typeName == "Decline":
                    rule_id = rule.typeId
        with allure.step(
            "Обновление узла рассчёта на различные ссылки на переменные в rule expression"
        ):
            rule_var = rule_set_var_const(
                is_arr=True,
                is_complex=True,
                var_name="rule_var",
                type_id=var_id,
                var_path=None,
                var_root_id=None,
            )
            rule_properties = rule_set_properties(
                apply_rule=True,
                rule_name="test_rule",
                rule_code="test",
                rule_type_id=rule_id,
                rule_description="made in test",
                rule_expression=expr,
                rule_weight_factor=1.0,
            )
            node_rule_upd = ruleset_node_construct(
                x=700,
                y=202.22915649414062,
                temp_version_id=template.versionId,
                rule_variable=rule_var,
                rules=[rule_properties],
                operation="update",
            )
            update_node(super_user, node_id=node_rule_id, body=node_rule_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_rule_upd.nodeTypeId,
                            properties=node_rule_upd.properties))
        with allure.step("Получение информации об узле"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_rule_id).body
            )
        with allure.step("Проверка валидации узла"):
            assert node_view.validFlag == valid
