import json
import pytest

import allure

from common.generators import generate_string
from products.Decision.framework.model import AggregateGetFullView, AggregateFunction1, ResponseDto, \
    AggregateGetFullVersionView
from products.Decision.framework.steps.decision_steps_aggregate_api import aggregate_list, create_aggregate \
    , get_aggregate, aggregate_versions
from products.Decision.utilities.aggregate_constructors import *


@allure.epic("Агрегаты")
@allure.feature("Информация об агрегатах")
class TestAggregatesInfo:

    @allure.story("В списке агрегатов присутствуют Наименование агрегата, Описание агрегата,"
                  " Функция агрегата, Тип значения агрегата, Группирующий элемент, Расчет агрегата,"
                  " Чтение агрегата")
    @allure.title("Получить список агрегатов, проверить наличие полей")
    @pytest.mark.scenario("DEV-15460")
    def test_list_aggregates(self, super_user, create_aggregate_gen):
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
            create_aggregate_gen.try_create_aggr(aggr_body=aggr_body)
        with allure.step("Получение списка агрегатов"):
            aggr_list = []
            list_response = aggregate_list(super_user).body["content"]
            for aggr in list_response:
                aggr_list.append(AggregateGetFullView.construct(**aggr))
        with allure.step("Проверка, что в списке содержится необходимая информация"):
            aggrs_contain_req_fields = next((aggr for aggr in aggr_list if
                                             aggr.aggregateJson is not None
                                             and aggr.objectName is not None
                                             and aggr.aggregateId is not None
                                             and aggr.versionId is not None), True)

            assert len(aggr_list) != 0 and aggrs_contain_req_fields

    @allure.story("При получении конкретного агрегата приходит информация о полях:"
                  " имя агрегата, описание агрегата, тип значения агрегата, агрегирующая функция,"
                  " группирующий элемент ")
    @allure.title("Получить информацию о конкретном агрегате, проверить поля с информацией")
    @pytest.mark.scenario("DEV-15460")
    def test_aggregate_info(self, super_user, create_aggregate_gen):
        with allure.step("Генерация данных агрегата"):
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(aggregate_name=aggr_name,
                                                 aggregate_variable_type="1",
                                                 aggregate_function=AggregateFunction1.AggAverage,
                                                 aggregate_description="created in test",
                                                 grouping_element="client")
            aggr_body = aggregate_construct(aggregate_name=aggr_name,
                                            aggregate_json=json.dumps(dict(aggr_json)),
                                            aggregate_description="created in test")
        with allure.step("Создание агрегата"):
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(aggr_body=aggr_body)
        with allure.step("Получение информации об агрегате"):
            search_result = AggregateGetFullView.construct(
                **get_aggregate(super_user, create_resp.uuid).body)
        with allure.step("Проверка, что в информации об агрегате отображаются нужные поля с корректной информацией"):
            assert search_result.aggregateId is not None \
                   and search_result.objectName == aggr_name \
                   and search_result.versionId == create_resp.uuid \
                   and search_result.aggregateDescription == "created in test" \
                   and search_result.aggregateJson is not None \
                   and search_result.changeDt is not None \
                   and search_result.createDt is not None

    @allure.story("Можно получить список диаграмм в которых используется агрегат, присутствуют поля:"
                  "“Тип”: расчет/чтение"
                  "Код диаграммы"
                  "Версия"
                  "Тип версии")
    @allure.title("Получить информацию о версиях агрегата, проверить поля с информацией")
    @pytest.mark.scenario("DEV-15460")
    def test_aggregate_info_versions(self, super_user, create_aggregate_gen):
        with allure.step("Генерация данных агрегата"):
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(aggregate_name=aggr_name,
                                                 aggregate_variable_type="1",
                                                 aggregate_function=AggregateFunction1.AggAverage,
                                                 aggregate_description="created in test",
                                                 grouping_element="client")
            aggr_body = aggregate_construct(aggregate_name=aggr_name,
                                            aggregate_json=json.dumps(dict(aggr_json)),
                                            aggregate_description="created in test")
        with allure.step("Создание агрегата"):
            create_resp: ResponseDto = create_aggregate_gen.create_aggr(aggr_body=aggr_body)
        with allure.step("Получение информации об агрегате"):
            search_result = AggregateGetFullView.construct(
                **get_aggregate(super_user, create_resp.uuid).body)
        with allure.step("Получение списка версий агрегата по agregateId"):
            vers_list = []
            for vers in aggregate_versions(super_user, search_result.aggregateId).body:
                vers_list.append(AggregateGetFullVersionView.construct(**vers))
        with allure.step("Проверка, что в информации о версии отображаются нужные поля с корректной информацией"):
            assert vers_list[0].aggregateId is not None \
                   and vers_list[0].objectName == aggr_name \
                   and vers_list[0].versionId == create_resp.uuid \
                   and vers_list[0].aggregateDescription == "created in test" \
                   and vers_list[0].aggregateJson is not None \
                   and vers_list[0].changeDt is not None \
                   and vers_list[0].createDt is not None \
                   and vers_list[0].versionType == "LATEST" \
                   and vers_list[0].versionName is not None
