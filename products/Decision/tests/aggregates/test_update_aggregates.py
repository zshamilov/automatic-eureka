import json

import glamor as allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import (
    AggregateFunction1,
    ResponseDto,
    AggregateGetFullView,
)
from products.Decision.framework.steps.decision_steps_aggregate_api import (
    update_aggregate,
    get_aggregate,
)
from products.Decision.tests.diagrams.test_add_diagrams import (
    generate_diagram_name_description,
)
from products.Decision.utilities.aggregate_constructors import *


@allure.epic("Агрегаты")
@allure.feature("Обновление агрегата")
class TestAggregatesUpdate:
    @allure.story("При обновлении агрегата, если ввести новые имя и описание агрегата,"
                  " они будут возвращаться в информации об агрегате")
    @allure.title("Обновить имя и описание агрегата")
    @pytest.mark.scenario("DEV-15460")
    def test_update_aggregate_name_description(self, super_user, create_aggregate_gen):
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
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(
                aggr_body=aggr_body
            )
        with allure.step("Генерация обновлённых имени и описания агрегата"):
            up_name = "aggregate_updated" + generate_string()
            up_description = "it was updated"
            up_json = aggregate_json_construct(
                aggregate_name=up_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description=up_description,
                grouping_element="client",
            )
            update_body = aggregate_update_construct(
                aggregate_name=up_name,
                aggregate_json=json.dumps(dict(up_json)),
                aggregate_description=up_description,
            )
        with allure.step("Обновление данных агрегата"):
            update_aggregate(
                super_user, aggregate_id=create_resp.uuid, body=update_body
            )
        with allure.step("Получение информации об агрегате"):
            search_result = AggregateGetFullView.construct(
                **get_aggregate(super_user, create_resp.uuid).body
            )
        with allure.step("Проверка, что имя и описание агрегата обновлены"):
            assert (
                search_result.aggregateDescription == up_description
                and search_result.objectName == up_name
            )

    @allure.story("При обновлении агрегата нельзя ввести имя длиной больше 100 символов")
    @allure.title("Проверить ограничение длины имени агрегата в 100 символов")
    @pytest.mark.scenario("DEV-15460")
    @pytest.mark.parametrize(
        "name, status",
        [
            (generate_diagram_name_description(99, 1)["rand_name"], True),
            (generate_diagram_name_description(100, 1)["rand_name"], True)
        ],
    )
    def test_update_aggregate_name_length(
        self, super_user, create_aggregate_gen, name, status
    ):
        updated = False
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
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(
                aggr_body=aggr_body
            )
        with allure.step("Подготовка изменённых данных с именами различной длины"):
            up_description = "it was updated"
            up_json = aggregate_json_construct(
                aggregate_name=name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description=up_description,
                grouping_element="client",
            )
            update_body = aggregate_update_construct(
                aggregate_name=name,
                aggregate_json=json.dumps(dict(up_json)),
                aggregate_description=up_description,
            )
        with allure.step("Обновление агрегата"):
            update_aggregate(
                super_user, aggregate_id=create_resp.uuid, body=update_body
            )
        with allure.step("Получение информации об агрегате"):
            search_result = AggregateGetFullView.construct(
                **get_aggregate(super_user, create_resp.uuid).body
            )
            if search_result.objectName == name:
                updated = True
        with allure.step(
            "Проверка, что имя обновилось или нет согласно проверяемой длинне"
        ):
            assert updated == status

    @allure.story("При обновлении агрегата нельзя ввести описание длиной больше 1000 символов")
    @allure.title("Обновить имя и описание агрегата")
    @pytest.mark.scenario("DEV-15460")
    @pytest.mark.parametrize(
        "description, status",
        [
            (generate_diagram_name_description(8, 999)["rand_description"], True),
            (generate_diagram_name_description(8, 1000)["rand_description"], True),
            ("", True)
        ],
    )
    def test_update_aggregate_descr_length(
        self, super_user, create_aggregate_gen, description, status
    ):
        updated = False
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
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(
                aggr_body=aggr_body
            )
        with allure.step("Подготовка изменённых данных с описаниями различной длины"):
            up_name = "aggregate_updated" + generate_string()
            up_json = aggregate_json_construct(
                aggregate_name=up_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggAverage,
                aggregate_description=description,
                grouping_element="client",
            )
            update_body = aggregate_update_construct(
                aggregate_name=up_name,
                aggregate_json=json.dumps(dict(up_json)),
                aggregate_description=description,
            )
        with allure.step("Обновление агрегата"):
            update_aggregate(
                super_user, aggregate_id=create_resp.uuid, body=update_body
            )
        with allure.step("Получение информации об агрегате"):
            search_result = AggregateGetFullView.construct(
                **get_aggregate(super_user, create_resp.uuid).body
            )
            if search_result.aggregateDescription == description:
                updated = True
        with allure.step(
            "Проверка, что описание обновилось или нет согласно проверяемой длинне"
        ):
            assert updated == status

    @allure.story("При обновлении агрегата можно изменить параметры агрегата:"
                  " Тип значения агрегата, Агрегирующая функция, Группирующий элемент")
    @allure.title("Обновить json с настройками агрегата")
    @pytest.mark.scenario("DEV-15460")
    def test_update_aggregate_json(self, super_user, create_aggregate_gen):
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
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(
                aggr_body=aggr_body
            )
        with allure.step("Подготовка изменённого json"):
            up_name = "aggregate_updated" + generate_string()
            up_description = "it was updated"
            up_json = aggregate_json_construct(
                aggregate_name=up_name,
                aggregate_variable_type="0",
                aggregate_function=AggregateFunction1.AggMin,
                aggregate_description=up_description,
                grouping_element="Client ID",
            )
            update_body = aggregate_update_construct(
                aggregate_name=up_name,
                aggregate_json=json.dumps(dict(up_json)),
                aggregate_description=up_description,
            )
        with allure.step("Обновление агрегата"):
            update_aggregate(
                super_user, aggregate_id=create_resp.uuid, body=update_body
            )
        with allure.step("Получение информации об агрегате"):
            search_result = AggregateGetFullView.construct(
                **get_aggregate(super_user, create_resp.uuid).body
            )
            actual_json = json.loads(search_result.aggregateJson)
            actual_json_model = AggregateJson.construct(**actual_json)
        with allure.step(
            "Проверка, что json агрегата с параметрами указанными при обновлении"
        ):
            assert (
                actual_json_model.aggregateFunction == AggregateFunction1.AggMin
                and actual_json_model.groupingElement == "Client ID"
                and actual_json_model.aggregateVariableType == "0"
            )
