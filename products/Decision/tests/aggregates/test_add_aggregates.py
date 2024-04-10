import json

import glamor as allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import (
    AggregateFunction1,
    ResponseDto,
    AggregateGetFullView, AggregateGetFullVersionView,
)
from products.Decision.framework.steps.decision_steps_aggregate_api import (
    aggregate_list, get_grouping_elements_list, aggregate_versions,
)
from products.Decision.tests.diagrams.test_add_diagrams import (
    generate_diagram_name_description,
)
from products.Decision.utilities.aggregate_constructors import *


@allure.epic("Агрегаты")
@allure.feature("Добавление агрегата")
class TestAggregatesAdd:
    @allure.story("Агрегат возможно создать, если при создании заполнить Имя,"
                  " и параметры агрегата: Тип значения агрегата, Агрегирующая функция, Группирующий элемент")
    @allure.title("создать аггрегат, проверить, что создан")
    @pytest.mark.scenario("DEV-15460")
    def test_create_aggregate(self, super_user, create_aggregate_gen):
        with allure.step("получение группирующих элементов агрегата"):
            grouping_element = "element for test"
        with allure.step("Генерация данных агрегата"):
            aggregate_created = False
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(
                aggregate_name=aggr_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggCount,
                aggregate_description="created in test",
                grouping_element=f"{grouping_element}",
            )
            aggr_body = aggregate_construct(
                aggregate_name=aggr_name,
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description="created in test",
            )
        with allure.step("Создание агрегата"):
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(
                aggr_body=aggr_body
            )
        with allure.step("Получение списка агрегатов"):
            aggr_list = []
            list_response = aggregate_list(super_user, agr_name=aggr_name).body["content"]
            for aggr in list_response:
                aggr_list.append(AggregateGetFullView.construct(**aggr))
            for aggregate in aggr_list:
                if aggregate.versionId == create_resp.uuid:
                    aggregate_created = True
        with allure.step("Проверка, что созданный агрегат появился в списке"):
            assert aggregate_created

    @allure.story("При создании имя агрегата не должно превышать 100 символов")
    @allure.title("Проверить ограничение имени аггрегата по длине")
    @pytest.mark.scenario("DEV-15460")
    @pytest.mark.parametrize(
        "name, status",
        [
            (generate_diagram_name_description(99, 1, 'auto_test_aggregate_')["rand_name"], True),
            (generate_diagram_name_description(100, 1, 'auto_test_aggregate_')["rand_name"], True),
        ],
    )
    def test_aggregate_name(self, super_user, create_aggregate_gen, name, status):
        aggregate_created = False
        with allure.step("Генерация данных агрегата"):
            aggr_name = name
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
        with allure.step("Создание агрегата с именем заданной длины"):
            create_resp = create_aggregate_gen.try_create_aggr(aggr_body=aggr_body)
            create_result: ResponseDto = ResponseDto.construct(**create_resp.body)
            aggr_list = []
            list_response = aggregate_list(super_user, agr_name=aggr_name).body["content"]
            for aggr in list_response:
                aggr_list.append(AggregateGetFullView.construct(**aggr))
            for aggregate in aggr_list:
                if aggregate.versionId == create_result.uuid:
                    aggregate_created = True
        with allure.step(
                "Проверка, что агрегат создался или нет в зависимости от длины имени"
        ):
            assert aggregate_created == status

    @allure.story("При создании описание агрегата не должно превышать 1000 символов")
    @allure.title("Проверить ограничение описания аггрегата по длине")
    @pytest.mark.scenario("DEV-15460")
    @allure.issue("DEV-6420")
    def test_aggregate_name_neg(
            self, super_user, create_aggregate_gen
    ):
        with allure.step("Генерация данных агрегата"):
            aggr_json = aggregate_json_construct(
                aggregate_name=generate_string(101),
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description="",
                grouping_element="client",
            )
            aggr_body = aggregate_construct(
                aggregate_name=generate_string(101),
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description="",
            )
        with allure.step(
                "Проверка, что агрегат создался или нет в зависимости от длины имени"
        ):
            with pytest.raises(HTTPError, match="400"):
                assert create_aggregate_gen.try_create_aggr(aggr_body=aggr_body)

    @allure.story("При создании описание агрегата не должно превышать 1000 символов")
    @allure.title("Проверить ограничение описания аггрегата по длине")
    @pytest.mark.scenario("DEV-15460")
    @pytest.mark.parametrize(
        "description, status",
        [
            (generate_diagram_name_description(8, 999)["rand_description"], True),
            (generate_diagram_name_description(8, 1000)["rand_description"], True)
        ],
    )
    def test_aggregate_description(
            self, super_user, create_aggregate_gen, description, status
    ):
        aggregate_created = False
        with allure.step("Генерация данных агрегата"):
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(
                aggregate_name=aggr_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description=description,
                grouping_element="client",
            )
            aggr_body = aggregate_construct(
                aggregate_name=aggr_name,
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description=description,
            )
        with allure.step("Создание агрегата с описанием заданной длины"):
            create_resp = create_aggregate_gen.try_create_aggr(aggr_body=aggr_body)
            create_result: ResponseDto = ResponseDto.construct(**create_resp.body)
            aggr_list = []
            list_response = aggregate_list(super_user, agr_name=aggr_name).body["content"]
            for aggr in list_response:
                aggr_list.append(AggregateGetFullView.construct(**aggr))
            for aggregate in aggr_list:
                if aggregate.versionId == create_result.uuid:
                    aggregate_created = True
        with allure.step(
                "Проверка, что агрегат создался или нет в зависимости от длины описания"
        ):
            assert aggregate_created == status

    @allure.story("При создании описание агрегата не должно превышать 1000 символов")
    @allure.title("Проверить ограничение описания аггрегата по длине")
    @pytest.mark.scenario("DEV-15460")
    @allure.issue("DEV-6420")
    def test_aggregate_description_neg(
            self, super_user, create_aggregate_gen
    ):
        aggregate_created = False
        with allure.step("Генерация данных агрегата"):
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(
                aggregate_name=aggr_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description=generate_diagram_name_description(8, 1001)["rand_description"],
                grouping_element="client",
            )
            aggr_body = aggregate_construct(
                aggregate_name=aggr_name,
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description=generate_diagram_name_description(8, 1001)["rand_description"],
            )
        with allure.step(
                "Проверка, что агрегат создался или нет в зависимости от длины описания"
        ):
            with pytest.raises(HTTPError, match="400"):
                assert create_aggregate_gen.try_create_aggr(aggr_body=aggr_body)

    @allure.story("Нельзя создать агрегат с именем, которое уже занято другим агрегатом")
    @allure.title(
        "Проверить, что нельзя создать агрегат с именем, которое уже занято другим агрегатом"
    )
    @pytest.mark.scenario("DEV-15460")
    @allure.issue("DEV-9974")
    def test_create_same_name_aggregate(
            self, super_user, create_aggregate_gen
    ):
        with allure.step("Создание информации об агрегате"):
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(
                aggregate_name=aggr_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description="test",
                grouping_element="client",
            )
            aggr_body = aggregate_construct(
                aggregate_name=aggr_name,
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description="test",
            )
        with allure.step("Создание template агрегата"):
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(
                aggr_body=aggr_body
            )
        with allure.step("Проверка отказа в создании агрегата с занятым именем"):
            with pytest.raises(HTTPError, match="400"):
                assert create_aggregate_gen.try_create_aggr(aggr_body=aggr_body)

    @allure.story(
        "При создании глобальной версии диаграммы с агрегатом, создаётся и глобальная версия агрегата"
    )
    @allure.title(
        "Создать глобальную версию диаграмму с агрегатом, найти в списке версий агрегата глобал-версию"
    )
    @pytest.mark.scenario("DEV-727")
    def test_create_aggregate_global_version(self, super_user,
                                             diagram_aggregate_compute_save, save_diagrams_gen):
        aggregate: AggregateGetFullView = diagram_aggregate_compute_save["aggregate"]
        diagram_id = diagram_aggregate_compute_save["diagram_id"]
        saved_version_id = diagram_aggregate_compute_save["saved_version_id"]
        new_diagram_name = diagram_aggregate_compute_save["diagram_name"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="diagram_user_version",
                    diagram_name=new_diagram_name,
                    global_flag=True,
                ).body
            )
        with allure.step("Поиск в списке версий агрегатов глобальной версии "):
            vers_list = []
            for vers in aggregate_versions(super_user, aggregate.aggregateId).body:
                vers_list.append(AggregateGetFullVersionView.construct(**vers))
            assert any(vers.versionType == "USER_GLOBAL" for vers in vers_list)
