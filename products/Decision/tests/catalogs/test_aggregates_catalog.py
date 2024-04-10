import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import AggregateGetFullView, AggregateCatalogGetFullView, ResponseDto, \
    CatalogCreate
from products.Decision.framework.steps.decision_steps_aggregate_api import delete_aggregate
from products.Decision.framework.steps.decision_steps_catalog import get_aggregates_catalog_content_by_id, \
    create_catalog, delete_catalogs, find_aggregate_in_aggregates_catalogs, move_element_in_catalog


@allure.epic("Каталоги")
@allure.feature("Каталоги. Агрегаты")
@pytest.mark.scenario("DEV-7849")
class TestCatalogAggregates:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать агрегат в каталоге, найти")
    @pytest.mark.smoke
    def test_create_aggregate_in_catalog(self, super_user, created_catalog_id, create_aggregate_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание агрегата в каталоге"):
            aggregate_in_catalog: AggregateGetFullView = create_aggregate_gen.create_aggr_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объекте в каталоге"):
            catalogs_object_info = AggregateCatalogGetFullView.construct(
                **get_aggregates_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Агрегат найден в каталоге"):
            assert catalogs_object_info.aggregateId == aggregate_in_catalog.aggregateId and \
                   catalogs_object_info.objectName == aggregate_in_catalog.objectName

    @allure.story("Объект возможно удалить из каталога")
    @allure.title("Удалить агрегат из каталога, проверить, что каталог пуст")
    @pytest.mark.smoke
    def test_delete_aggregate_in_catalog(self, super_user, created_catalog_id, create_aggregate_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание агрегата в каталоге"):
            aggregate_in_catalog: AggregateGetFullView = create_aggregate_gen.create_aggr_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Удаление агрегата в каталоге"):
            delete_aggregate(super_user, aggregate_in_catalog.versionId)
        with allure.step("Получение информации об объектах в каталоге"):
            catalogs_content = get_aggregates_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Объектов в каталоге не обнаружено"):
            assert catalogs_content.status == 204 and \
                   not catalogs_content.body

    @allure.story("При удалении каталога, объекты внутри него удаляются")
    @allure.title("Удалить каталог внутри которого находится агрегат, агрегат удалён")
    @pytest.mark.smoke
    def test_delete_catalog_aggregate_in_catalog_deleted(self, super_user,
                                                         create_aggregate_gen):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name)).body)
            catalog_id = str(create_resp.uuid)
        with allure.step("Создание агрегата в каталоге"):
            aggregate_in_catalog: AggregateGetFullView = create_aggregate_gen.create_aggr_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Удаление созданного каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Поиск агрегата"):
            found_type = find_aggregate_in_aggregates_catalogs(super_user, aggregate_in_catalog.versionId,
                                                               aggregate_name=aggregate_in_catalog.objectName)
        with allure.step("Агрегат не найден"):
            assert found_type is None

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и агрегат в каталоге, увидеть, что в каталоге агрегатов только агрегат")
    def test_only_aggregate_in_catalog(self, super_user, created_catalog_id,
                                       create_aggregate_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение агрегата в каталоге"):
            aggregate_in_catalog: AggregateGetFullView = create_aggregate_gen.create_aggr_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Сохранение диаграммы в каталоге"):
            save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге агрегатов"):
            catalogs_objects_info = get_aggregates_catalog_content_by_id(
                super_user, catalog_id).body["content"]
        with allure.step("В каталоге только один объект и это агрегат"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["aggregateId"] == aggregate_in_catalog.aggregateId for el in catalogs_objects_info)

    @allure.story("Агрегат без каталога возможно поместить в каталог")
    @allure.title("Создать агрегат и каталог, поместить агрегат в каталог")
    @pytest.mark.smoke
    def test_aggregate_in_catalog_move(self, super_user, created_catalog_id,
                                       create_aggregate_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение агрегата без каталога"):
            aggregate_without_catalog: AggregateGetFullView = create_aggregate_gen.create_aggr_in_catalog(
                catalog_id=None)
            aggregate_version_id = aggregate_without_catalog.versionId
        with allure.step("Поиск агрегата в списке каталогов агрегатов"):
            aggregate_element_id = find_aggregate_in_aggregates_catalogs(
                super_user, aggregate_version_id,
                aggregate_name=aggregate_without_catalog.objectName).elementId
        with allure.step("Перемещение агрегата в созданный каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id,
                                    element_id=aggregate_element_id)
        with allure.step("Получение информации о первом объекте в созданном каталоге"):
            catalogs_object_info = AggregateCatalogGetFullView.construct(
                **get_aggregates_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Агрегат найден в каталоге"):
            assert catalogs_object_info.aggregateId == aggregate_without_catalog.aggregateId and \
                   catalogs_object_info.objectName == aggregate_without_catalog.objectName

    @allure.story("Агрегат в каталоге возможно переместить в другой каталог")
    @allure.title("Создать два каталога и агрегат внутри первого, переместить агрегат из первого во второй каталог")
    @pytest.mark.smoke
    def test_aggregate_in_catalog_move_in_another_cat(self, super_user, created_two_catalogs,
                                                      create_aggregate_gen):
        catalog_id1 = created_two_catalogs["catalog_id1"]
        catalog_id2 = created_two_catalogs["catalog_id2"]
        with allure.step("Сохранение агрегата в первом каталоге"):
            aggregate_in_catalog1: AggregateGetFullView = create_aggregate_gen.create_aggr_in_catalog(
                catalog_id=catalog_id1)
            aggregate_version_id = aggregate_in_catalog1.versionId
        with allure.step("Поиск агрегата в первом каталоге агрегатов"):
            aggregate_element_id = find_aggregate_in_aggregates_catalogs(super_user, aggregate_version_id,
                                                                         catalog_id=catalog_id1).elementId
        with allure.step("Перемещение агрегата во второй каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id2,
                                    element_id=aggregate_element_id)
        with allure.step("Получение информации о первом объекте во втором каталоге"):
            second_catalogs_object_info = AggregateCatalogGetFullView.construct(
                **get_aggregates_catalog_content_by_id(super_user, catalog_id2).body["content"][0])
        with allure.step("Получение информации о контенте в первом каталоге"):
            first_catalog_content = get_aggregates_catalog_content_by_id(
                super_user, catalog_id1)
        with allure.step("Агрегат найден во втором каталоге, первый каталог пуст"):
            assert second_catalogs_object_info.aggregateId == aggregate_in_catalog1.aggregateId and \
                   second_catalogs_object_info.objectName == aggregate_in_catalog1.objectName and \
                   first_catalog_content.status == 204
