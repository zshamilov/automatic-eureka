import json
import pytest

import glamor as allure
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import (
    AggregateFunction1,
    ResponseDto,
    AggregateGetFullView, AggregateGetFullVersionView,
)
from products.Decision.framework.steps.decision_steps_aggregate_api import (
    create_aggregate,
    delete_aggregate,
    get_aggregate,
    aggregate_list, aggregate_versions, aggregate_list_content,
)
from products.Decision.utilities.aggregate_constructors import *


@allure.epic("Агрегаты")
@allure.feature("Удаление агрегата")
class TestAggregatesDelete:

    @allure.story("Невозможно получить информацию об удалённой версии агрегата")
    @allure.title("создать аггрегат, удалить, проверить, что не найден")
    @pytest.mark.scenario("DEV-15460")
    def test_delete_aggregate(self, super_user):
        with allure.step("Генерация данных агрегата"):
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(
                aggregate_name=aggr_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description="created in test",
                grouping_element="client",
            )
            aggr_body = aggregate_construct(
                aggregate_name=aggr_name,
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description="created in test",
            )
        with allure.step("Создание агрегата"):
            create_resp: ResponseDto = ResponseDto.construct(
                **create_aggregate(super_user, body=aggr_body).body
            )
        with allure.step("Удаление агрегата по id версии"):
            version_id = create_resp.uuid
            delete_aggregate(super_user, version_id)
        with allure.step("Проверка, что удалённая версия не найдена"):
            with pytest.raises(HTTPError, match="404"):
                assert get_aggregate(super_user, version_id)

    @allure.story("Удалённая Latest версия агрегата пропадает из списка агрегатов")
    @allure.title("создать аггрегат, удалить, проверить, что пропал из списка")
    @pytest.mark.scenario("DEV-727")
    def test_delete_aggregate_from_list(self, super_user):
        aggr_found = False
        with allure.step("Генерация данных агрегата"):
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(
                aggregate_name=aggr_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description="created in test",
                grouping_element="client",
            )
            aggr_body = aggregate_construct(
                aggregate_name=aggr_name,
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description="created in test",
            )
        with allure.step("Создание агрегата"):
            create_resp: ResponseDto = ResponseDto.construct(
                **create_aggregate(super_user, body=aggr_body).body
            )
        with allure.step("Удаление агрегата по id версии"):
            version_id = create_resp.uuid
            delete_aggregate(super_user, version_id)
        with allure.step("Получение списка агрегатов"):
            aggr_list = aggregate_list_content(super_user)
        with allure.step(
                "Проверка, что удалённая latest версия пропала из списка аггрегатов"
        ):
            for aggr in aggr_list:
                if aggr["versionId"] == version_id:
                    aggr_found = True
            assert not aggr_found

    @allure.story(
        "Невозможно удалить глобал-версию агрегата"
    )
    @allure.issue("DEV-12301")
    @pytest.mark.scenario("DEV-727")
    @allure.title(
        "Удалить глобальную версию агрегата, проверить, что запрещено"
    )
    def test_delete_aggregate_global_version(self, super_user,
                                             diagram_aggregate_compute_save, save_diagrams_gen):
        aggregate: AggregateGetFullView = diagram_aggregate_compute_save["aggregate"]
        diagram_id = diagram_aggregate_compute_save["diagram_id"]
        saved_version_id = diagram_aggregate_compute_save["saved_version_id"]
        new_diagram_name = diagram_aggregate_compute_save["diagram_name"]
        with allure.step("Создание глобальной версии диаграммы с агрегатом"):
            gv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="diagram_user_version",
                    diagram_name=new_diagram_name,
                    global_flag=True,
                ).body
            )
        version_id = None
        aggregates = []
        for aggr in aggregate_versions(super_user, aggregate.aggregateId).body:
            aggregates.append(AggregateGetFullVersionView.construct(**aggr))
        for aggr in aggregates:
            if aggr.versionType == "USER_GLOBAL":
                version_id = aggr.versionId

        with allure.step("Нельзя удалять глобальные версии агрегатов"):
            with pytest.raises(HTTPError, match="400"):
                assert delete_aggregate(super_user, version_id)
