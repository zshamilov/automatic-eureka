import uuid

import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    DiagramViewDto,
    JoinConditionType,
    ResponseDto,
    NodeViewWithVariablesDto, NodeValidateDto,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    validate_diagram, )
from products.Decision.framework.steps.decision_steps_nodes import (
    update_node,
    get_node_by_id,
    delete_link_by_id,
    possible_nodes,
    previous_nodes,
)
from products.Decision.utilities.node_cunstructors import (
    default_branch,
    fork_node_construct,
    join_branch,
    join_node_construct,
)


@allure.epic("Диаграммы")
@allure.feature("Узлы fork, join")
class TestDiagramsForkJoinNodes:
    @allure.story("Узел можно обновить с соответствии с json схемой узла")
    @allure.title(
        "Проверить, что в диаграмме с корректной связью fork join, в информации об узле fork передается "
        "корректная информация"
    )
    @pytest.mark.scenario("DEV-15451")
    @pytest.mark.smoke
    def test_fork_node_correct(self, super_user, diagram_fork_join):
        template: DiagramViewDto = diagram_fork_join["diagram_template"]
        node_fork_id = diagram_fork_join["node_fork_id"]
        node_join_id = diagram_fork_join["node_join_id"]
        node_calc1_id = diagram_fork_join["node_calc1_id"]
        node_calc2_id = diagram_fork_join["node_calc2_id"]
        link_f_c1_id = diagram_fork_join["link_f_c1_id"]
        link_f_c2_id = diagram_fork_join["link_f_c2_id"]
        with allure.step("Обновление узла fork на корректные данные"):
            fork_branch1 = default_branch(node_calc1_id, link_id=link_f_c1_id)
            fork_branch2 = default_branch(node_calc2_id, link_id=link_f_c2_id)
            def_branch = default_branch(node_join_id)
            node_fork_up_body = fork_node_construct(
                x=304,
                y=246,
                temp_version_id=template.versionId,
                branches=[fork_branch1, fork_branch2],
                default_join_path=def_branch,
                node_ids_with_join_node_ids=[node_calc1_id, node_calc2_id, ""],
                operation="update",
            )
            update_node(super_user, node_id=node_fork_id, body=node_fork_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_fork_up_body.nodeTypeId,
                            properties=node_fork_up_body.properties))
        with allure.step("Обновление узла join на корректные данные"):
            join_branch1 = join_branch(path=node_calc1_id, priority=1)
            join_branch2 = join_branch(path=node_calc2_id, priority=2)
            node_join_up_body = join_node_construct(
                x=1200,
                y=246,
                temp_version_id=template.versionId,
                branches=[join_branch1, join_branch2],
                join_condition_type=JoinConditionType.COMPLETION_OF_ALL_PREVIOUS_BLOCKS,
                timeout=60,
                operation="update",
            )
            update_node(super_user, node_id=node_join_id, body=node_join_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_join_up_body.nodeTypeId,
                            properties=node_join_up_body.properties))
        with allure.step("Получение информации об узле fork"):
            node_fork_view: NodeViewWithVariablesDto = (
                NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, node_fork_id).body
                )
            )
        with allure.step(
            "Проверка, что ветви и узлы, связанные с узлом join корректны"
        ):
            fork_branch_correct = 0
            fork_nodes_with_join_correct = 0
            for branch in node_fork_view.properties["branches"]:
                if (
                    branch["nodeId"] == fork_branch1.nodeId
                    and branch["linkId"] == fork_branch1.linkId
                ):
                    fork_branch_correct += 1
                if (
                    branch["nodeId"] == fork_branch2.nodeId
                    and branch["linkId"] == fork_branch2.linkId
                ):
                    fork_branch_correct += 1
            for node_id in node_fork_view.properties["nodeIdsWithJoinNodeIds"]:
                if node_id == node_calc2_id:
                    fork_nodes_with_join_correct += 1
                if node_id == node_calc1_id:
                    fork_nodes_with_join_correct += 1
                if node_id == node_join_id:
                    fork_nodes_with_join_correct += 1
            assert (
                fork_branch_correct == 2
                and fork_nodes_with_join_correct == 3
                and node_fork_view.properties["defaultJoinPath"]["nodeId"]
                == node_join_id
                and node_fork_view.validFlag
            )

    @allure.story("Блок Fork обязательно должен ссылаться на блок Join")
    @allure.title(
        "Проверить, что валидация узла fork срабатывает при указании недопустимого парного узла в узле fork"
    )
    @pytest.mark.scenario("DEV-15451")
    @allure.issue("DEV-6572")
    @pytest.mark.smoke
    def test_fork_valid_if_join_valid(self, super_user, diagram_fork_join):
        with allure.step(
            "Создание диаграммы с узлами начало, fork, рассчёт1, рассчёт2, join, завершение и связями в "
            "них"
        ):
            template: DiagramViewDto = diagram_fork_join["diagram_template"]
            node_fork_id = diagram_fork_join["node_fork_id"]
            node_join_id = diagram_fork_join["node_join_id"]
            node_calc1_id = diagram_fork_join["node_calc1_id"]
            node_calc2_id = diagram_fork_join["node_calc2_id"]
            link_f_c1_id = diagram_fork_join["link_f_c1_id"]
            link_f_c2_id = diagram_fork_join["link_f_c2_id"]
        with allure.step("Подготовка данных для обновления узла fork"):
            fork_branch1 = default_branch(node_calc1_id, link_id=link_f_c1_id)
            fork_branch2 = default_branch(node_calc2_id, link_id=link_f_c2_id)
            def_branch = default_branch(str(uuid.uuid4()))
            node_fork_up_body = fork_node_construct(
                x=304,
                y=246,
                temp_version_id=template.versionId,
                branches=[fork_branch1, fork_branch2],
                default_join_path=def_branch,
                node_ids_with_join_node_ids=[node_calc1_id, node_calc2_id, ""],
                operation="update",
            )
        with allure.step(
            "Обновление узла fork с проставлением несуществующего иденификатора парного узла"
        ):
            update_node(super_user, node_id=node_fork_id, body=node_fork_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_fork_up_body.nodeTypeId,
                            properties=node_fork_up_body.properties))
        with allure.step("Получение информации об узле fork"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_fork_id).body
            )
        with allure.step(
            "Проверка, что узел fork не валиден так как ссылается на несуществующий узел"
        ):
            assert node_view.validFlag == False

    @allure.story(
        "Один блок слияния не может принимать на вход ветви непарного ему блока распараллеливания"
    )
    @allure.title(
        "Проверить, что валидация узла join срабатывает при указании недопустимого парного узла в узле fork"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-6572")
    @pytest.mark.smoke
    def test_join_valid_if_fork_valid(self, super_user, diagram_fork_join):
        with allure.step(
            "Создание диаграммы с узлами начало, fork, рассчёт1, рассчёт2, join, завершение и связями в "
            "них"
        ):
            template: DiagramViewDto = diagram_fork_join["diagram_template"]
            node_fork_id = diagram_fork_join["node_fork_id"]
            node_join_id = diagram_fork_join["node_join_id"]
            node_calc1_id = diagram_fork_join["node_calc1_id"]
            node_calc2_id = diagram_fork_join["node_calc2_id"]
            link_f_c1_id = diagram_fork_join["link_f_c1_id"]
            link_f_c2_id = diagram_fork_join["link_f_c2_id"]
        with allure.step("Подготовка данных для обновления узла fork"):
            fork_branch1 = default_branch(node_calc1_id, link_id=link_f_c1_id)
            fork_branch2 = default_branch(node_calc2_id, link_id=link_f_c2_id)
            def_branch = default_branch(str(uuid.uuid4()))
            node_fork_up_body = fork_node_construct(
                x=304,
                y=246,
                temp_version_id=template.versionId,
                branches=[fork_branch1, fork_branch2],
                default_join_path=def_branch,
                node_ids_with_join_node_ids=[node_calc1_id, node_calc2_id, ""],
                operation="update",
            )
        with allure.step(
            "Обновление узла fork с проставлением несуществующего иденификатора парного узла"
        ):
            update_node(super_user, node_id=node_fork_id, body=node_fork_up_body)
        with allure.step("Обновление узла join"):
            join_branch1 = join_branch(path=node_calc1_id, priority=1)
            join_branch2 = join_branch(path=node_calc2_id, priority=2)
            node_join_up_body = join_node_construct(
                x=1200,
                y=246,
                temp_version_id=template.versionId,
                branches=[join_branch1, join_branch2],
                join_condition_type=JoinConditionType.COMPLETION_OF_ALL_PREVIOUS_BLOCKS,
                timeout=60,
                operation="update",
            )
            update_node(super_user, node_id=node_join_id, body=node_join_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_join_up_body.nodeTypeId,
                            properties=node_join_up_body.properties))
        with allure.step("Получение информации об узле join"):
            node_join_view: NodeViewWithVariablesDto = (
                NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, node_join_id).body
                )
            )
        with allure.step(
            "проверка, что узел Join невалиден так как узел Fork не ссылается на него"
        ):
            with pytest.raises(HTTPError):
                assert validate_diagram(super_user, version_id=template.versionId).status == 422

    @allure.story(
        "Узел Распараллеливание потока должен иметь одинаковое количество выходящих потоков с количеством "
        "выходящих связей"
    )
    @allure.title(
        "Проверить, что валидация срабатывает при задании некорректных связей для узла fork"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.smoke
    def test_invalid_branches_fork(self, super_user, diagram_fork_join):
        template: DiagramViewDto = diagram_fork_join["diagram_template"]
        node_fork_id = diagram_fork_join["node_fork_id"]
        node_join_id = diagram_fork_join["node_join_id"]
        node_calc1_id = diagram_fork_join["node_calc1_id"]
        node_calc2_id = diagram_fork_join["node_calc2_id"]
        link_f_c1_id = diagram_fork_join["link_f_c1_id"]
        link_f_c2_id = diagram_fork_join["link_f_c2_id"]
        with allure.step("Обновление узла fork"):
            fork_branch1 = default_branch(node_calc1_id, link_id=link_f_c1_id)
            fork_branch2 = default_branch(node_calc2_id, link_id=link_f_c2_id)
            def_branch = default_branch(node_join_id)
            node_fork_up_body = fork_node_construct(
                x=304,
                y=246,
                temp_version_id=template.versionId,
                branches=[fork_branch1, fork_branch2],
                default_join_path=def_branch,
                node_ids_with_join_node_ids=[node_calc1_id, node_calc2_id, ""],
                operation="update",
            )
            update_node(super_user, node_id=node_fork_id, body=node_fork_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_fork_up_body.nodeTypeId,
                            properties=node_fork_up_body.properties))
        with allure.step("Обновление узла join"):
            join_branch1 = join_branch(path=node_calc1_id, priority=1)
            join_branch2 = join_branch(path=node_calc2_id, priority=2)
            node_join_up_body = join_node_construct(
                x=1200,
                y=246,
                temp_version_id=template.versionId,
                branches=[join_branch1, join_branch2],
                join_condition_type=JoinConditionType.COMPLETION_OF_ALL_PREVIOUS_BLOCKS,
                timeout=60,
                operation="update",
            )
            update_node(super_user, node_id=node_join_id, body=node_join_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_join_up_body.nodeTypeId,
                            properties=node_join_up_body.properties))
        with allure.step("Удаление связи из узла fork к одному из узлов расчёта"):
            delete_link_by_id(super_user, link_f_c2_id)
        with allure.step(
                "проверка, что узел Fork невалиден"
        ):
            with pytest.raises(HTTPError):
                assert validate_diagram(super_user, version_id=template.versionId).status == 422

    @allure.story("В Узле join параметр timeout должен быть положительным")
    @allure.title(
        "Проверить, что валидация срабатывает на недопустимых знаечниях timeout в узле Join"
    )
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.smoke
    def test_invalid_params_timeout_join(self, super_user, diagram_fork_join):
        template: DiagramViewDto = diagram_fork_join["diagram_template"]
        node_fork_id = diagram_fork_join["node_fork_id"]
        node_join_id = diagram_fork_join["node_join_id"]
        node_calc1_id = diagram_fork_join["node_calc1_id"]
        node_calc2_id = diagram_fork_join["node_calc2_id"]
        link_f_c1_id = diagram_fork_join["link_f_c1_id"]
        link_f_c2_id = diagram_fork_join["link_f_c2_id"]
        with allure.step("Обновление узла fork"):
            fork_branch1 = default_branch(node_calc1_id, link_id=link_f_c1_id)
            fork_branch2 = default_branch(node_calc2_id, link_id=link_f_c2_id)
            def_branch = default_branch(node_join_id)
            node_fork_up_body = fork_node_construct(
                x=304,
                y=246,
                temp_version_id=template.versionId,
                branches=[fork_branch1, fork_branch2],
                default_join_path=def_branch,
                node_ids_with_join_node_ids=[node_calc1_id, node_calc2_id, ""],
                operation="update",
            )
            update_node(super_user, node_id=node_fork_id, body=node_fork_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_fork_up_body.nodeTypeId,
                            properties=node_fork_up_body.properties))
        with allure.step("Обновление узла join с отрицательным значением timeout"):
            join_branch1 = join_branch(path=node_calc1_id, priority=1)
            join_branch2 = join_branch(path=node_calc2_id, priority=2)
            node_join_up_body = join_node_construct(
                x=1200,
                y=246,
                temp_version_id=template.versionId,
                branches=[join_branch1, join_branch2],
                join_condition_type=JoinConditionType.COMPLETION_OF_ALL_PREVIOUS_BLOCKS,
                timeout=-60,
                operation="update",
            )
            update_node(super_user, node_id=node_join_id, body=node_join_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_join_up_body.nodeTypeId,
                            properties=node_join_up_body.properties))

        with allure.step("Получение информации об узле join"):
            node_join_view: NodeViewWithVariablesDto = (
                NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, node_join_id).body
                )
            )
        with allure.step("Проверка, что узел не прошёл валидацию"):
            assert node_join_view.validFlag == False

    @allure.story(
        "В Узле слияния обязательно должен быть выставлен приоритет узлов и он не может быть одинаковым"
    )
    @allure.title(
        "Проверить, что валидация срабатывает на недопустимых значениях приоритета"
    )
    @pytest.mark.scenario("DEV-6398")
    @allure.issue("DEV-6574")
    @pytest.mark.parametrize("priority", [1, -2, None])
    def test_invalid_params_priority_join(
        self, super_user, diagram_fork_join, priority
    ):
        template: DiagramViewDto = diagram_fork_join["diagram_template"]
        node_fork_id = diagram_fork_join["node_fork_id"]
        node_join_id = diagram_fork_join["node_join_id"]
        node_calc1_id = diagram_fork_join["node_calc1_id"]
        node_calc2_id = diagram_fork_join["node_calc2_id"]
        link_f_c1_id = diagram_fork_join["link_f_c1_id"]
        link_f_c2_id = diagram_fork_join["link_f_c2_id"]
        with allure.step("Обновление узла fork"):
            fork_branch1 = default_branch(node_calc1_id, link_id=link_f_c1_id)
            fork_branch2 = default_branch(node_calc2_id, link_id=link_f_c2_id)
            def_branch = default_branch(node_join_id)
            node_fork_up_body = fork_node_construct(
                x=304,
                y=246,
                temp_version_id=template.versionId,
                branches=[fork_branch1, fork_branch2],
                default_join_path=def_branch,
                node_ids_with_join_node_ids=[node_calc1_id, node_calc2_id, ""],
                operation="update",
            )
            update_node(super_user, node_id=node_fork_id, body=node_fork_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_fork_up_body.nodeTypeId,
                            properties=node_fork_up_body.properties))
        with allure.step("Обновление узла join с недопустимыми значениями приоритета"):
            join_branch1 = join_branch(path=node_calc1_id, priority=1)
            join_branch2 = join_branch(path=node_calc2_id, priority=priority)
            node_join_up_body = join_node_construct(
                x=1200,
                y=246,
                temp_version_id=template.versionId,
                branches=[join_branch1, join_branch2],
                join_condition_type=JoinConditionType.COMPLETION_OF_ALL_PREVIOUS_BLOCKS,
                timeout=60,
                operation="update",
            )
            update_node(super_user, node_id=node_join_id, body=node_join_up_body,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_join_up_body.nodeTypeId,
                            properties=node_join_up_body.properties))

        with allure.step("Получение информации об узле join"):
            node_join_view: NodeViewWithVariablesDto = (
                NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, node_join_id).body
                )
            )
        with allure.step("Проверка, что узел join не прошёл валидацию"):
            assert node_join_view.validFlag == False

    @allure.story(
        "Для Узела распараллеливания потоков должны отображаться доступные для ссылания узлы"
    )
    @allure.title(
        "Проверить, что все узлы после узла fork отображаются возможными для связи"
    )
    @pytest.mark.scenario("DEV-15451")
    @pytest.mark.smoke
    def test_get_possible_for_fork(self, super_user, diagram_fork_join):
        template: DiagramViewDto = diagram_fork_join["diagram_template"]
        node_fork_id = diagram_fork_join["node_fork_id"]
        node_end_id = diagram_fork_join["node_end_id"]
        node_join_id = diagram_fork_join["node_join_id"]
        node_calc1_id = diagram_fork_join["node_calc1_id"]
        node_calc2_id = diagram_fork_join["node_calc2_id"]
        with allure.step("Получение информации о возможных узлах для узла fork"):
            pos_nodes = possible_nodes(
                super_user, node_fork_id, query={"diagramId": template.versionId}
            ).body
            assert_nodes_count = 0
            for node in pos_nodes:
                if (
                    node["nodeId"] == node_join_id
                    and node["nodeName"] == "Слияние потоков"
                ):
                    assert_nodes_count += 1
                if (
                    node["nodeId"] == node_calc1_id
                    and node["nodeName"] == "Расчет переменных"
                ):
                    assert_nodes_count += 1
                if (
                    node["nodeId"] == node_calc2_id
                    and node["nodeName"] == "Расчет переменных"
                ):
                    assert_nodes_count += 1
                if node["nodeId"] == node_end_id and node["nodeName"] == "Завершение":
                    assert_nodes_count += 1
            with allure.step("Проверка, что отображаются все доступные узлы"):
                assert len(pos_nodes) == 4 and assert_nodes_count == 4

    @allure.story("Для Узла слияния должны отображаться предыдущие узлы, "
                  "которые могут сойтись в Узле слияния, выходящие из Узла распараллеливания")
    @allure.title(
        "Проверить, что для блока join доступны два узла, выходящих из блока fork"
    )
    @pytest.mark.scenario("DEV-15451")
    @pytest.mark.smoke
    def test_get_previous_for_join(self, super_user, diagram_fork_join):
        template: DiagramViewDto = diagram_fork_join["diagram_template"]
        node_join_id = diagram_fork_join["node_join_id"]
        node_calc1_id = diagram_fork_join["node_calc1_id"]
        node_calc2_id = diagram_fork_join["node_calc2_id"]
        with allure.step("Получение информации о возможных узлах для узла fork"):
            pos_nodes = previous_nodes(
                super_user, node_join_id, query={"diagramVersionId": template.versionId}
            ).body
            assert_nodes_count = 0
            for node in pos_nodes:
                if (
                    node["nodeId"] == node_calc1_id
                    and node["nodeName"] == "Расчет переменных"
                ):
                    assert_nodes_count += 1
                if (
                    node["nodeId"] == node_calc2_id
                    and node["nodeName"] == "Расчет переменных"
                ):
                    assert_nodes_count += 1
            with allure.step("Проверка, чо отображаются все доступные узлы"):
                assert len(pos_nodes) == 2 and assert_nodes_count == 2
