import allure
import pytest

from products.Decision.framework.model import OfferFullViewDto, DiagramShortInfoView
from products.Decision.framework.steps.decision_steps_catalog import get_offers_catalog_content_by_id, delete_catalogs, \
    find_offer_in_offers_catalogs, move_element_in_catalog
from products.Decision.framework.steps.decision_steps_offer_api import delete_offer


@allure.epic("Каталоги")
@allure.feature("Каталоги. Шаблоны предложений")
@pytest.mark.scenario("DEV-7849")
class TestCatalogOffers:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать Шаблон предложения в каталоге, найти")
    @pytest.mark.smoke
    def test_create_offer_in_catalog(self, super_user, created_catalog_id,
                                     create_offer_gen):
        catalog_id = created_catalog_id

        with allure.step("Создание шаблона предложения в каталоге"):
            offer_in_catalog: OfferFullViewDto = create_offer_gen.create_full_offer(catalog_id=catalog_id)["offer_info"]

        with allure.step("Получение информации об объекте в каталоге"):
            catalogs_object_info = DiagramShortInfoView.construct(
                **get_offers_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Шаблон предложения найден в каталоге"):
            assert catalogs_object_info.versionId == offer_in_catalog.versionId

    @allure.story("Объект возможно удалить из каталога")
    @allure.title("Удалить шаблон предложения из каталога, проверить, что каталог пуст")
    @pytest.mark.smoke
    def test_delete_offer_in_catalog(self, super_user, created_catalog_id,
                                     create_offer_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание шаблона в каталоге"):
            offer_in_catalog: OfferFullViewDto = create_offer_gen.create_full_offer(catalog_id=catalog_id)["offer_info"]
        with allure.step("Удаление шаблона в каталоге"):
            delete_offer(super_user, offer_in_catalog.versionId)
        with allure.step("Получение информации об объектах в каталоге"):
            catalogs_object_info = get_offers_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Объектов в каталоге не обнаружено"):
            assert catalogs_object_info.status == 204

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и шаблон предложения в каталоге, увидеть,"
                  " что в каталоге шаблонов только шаблон")
    def test_only_offer_in_catalog(self, super_user, created_catalog_id,
                                   create_offer_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание шаблона в каталоге"):
            offer_in_catalog: OfferFullViewDto = create_offer_gen.create_full_offer(catalog_id=catalog_id)["offer_info"]
        with allure.step("Сохранение диаграммы в каталоге"):
            save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге шаблонов"):
            catalogs_objects_info = get_offers_catalog_content_by_id(super_user, catalog_id).body["content"]
        with allure.step("В каталоге только один объект и это шаблон"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["versionId"] == offer_in_catalog.versionId for el in catalogs_objects_info)

    @allure.story("При удалении каталога, объекты внутри него удаляются")
    @allure.title("Удалить каталог внутри которого находится сервис, сервис удалён")
    @pytest.mark.smoke
    def test_delete_catalog_offer_in_catalog_deleted(self, super_user, created_catalog_id,
                                                     create_offer_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание шаблона в каталоге"):
            offer_in_catalog: OfferFullViewDto = create_offer_gen.create_full_offer(catalog_id=catalog_id)["offer_info"]
        with allure.step("Удаление созданного каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Поиск шаблона"):
            found_service = find_offer_in_offers_catalogs(super_user, offer_in_catalog.versionId)
        with allure.step("Шаблон не найден"):
            assert found_service is None

    @allure.story("Шаблон в каталоге возможно переместить в другой каталог")
    @allure.title("Создать два каталога и шаблон внутри первого, переместить шаблон из первого во второй каталог")
    @pytest.mark.smoke
    def test_offer_in_catalog_move_in_another_cat(self, super_user, created_two_catalogs,
                                                  create_offer_gen):
        catalog_id1 = created_two_catalogs["catalog_id1"]
        catalog_id2 = created_two_catalogs["catalog_id2"]
        with allure.step("Сохранение шаблона в первом каталоге"):
            offer_in_catalog1: OfferFullViewDto = create_offer_gen.create_full_offer \
                (catalog_id=catalog_id1)["offer_info"]
            offer_version_id = offer_in_catalog1.versionId
        with allure.step("Поиск шаблона в первом каталоге шаблонов"):
            service_element_id = find_offer_in_offers_catalogs \
                (super_user, offer_version_id, catalog_id=catalog_id1).elementId
        with allure.step("Перемещение шаблона во второй каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id2,
                                    element_id=service_element_id)
        with allure.step("Получение информации о первом объекте во втором каталоге"):
            second_catalogs_object_info = DiagramShortInfoView.construct(
                **get_offers_catalog_content_by_id(super_user, catalog_id2).body["content"][0])
        with allure.step("Получение информации о контенте в первом каталоге"):
            first_catalog_content = get_offers_catalog_content_by_id(
                super_user, catalog_id1)
        with allure.step("Шаблон найден во втором каталоге, первый каталог пуст"):
            assert second_catalogs_object_info.versionId == offer_in_catalog1.versionId and \
                   first_catalog_content.status == 204

    @allure.story("Шаблон без каталога возможно поместить в каталог")
    @allure.title("Создать шаблон и каталог, поместить шаблон в каталог")
    @pytest.mark.smoke
    def test_offer_in_catalog_move(self, super_user, created_catalog_id,
                                   create_offer_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение шаблона без каталога"):
            offer_without_catalog: OfferFullViewDto = create_offer_gen.create_full_offer()["offer_info"]
            offer_version_id = offer_without_catalog.versionId
        with allure.step("Поиск шаблона в списке каталога шаблонов"):
            offer_element_id = find_offer_in_offers_catalogs(
                super_user, offer_version_id, offer_name=offer_without_catalog.objectName).elementId
        with allure.step("Перемещение шаблона в созданный каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id,
                                    element_id=offer_element_id)
        with allure.step("Получение информации о первом объекте в созданном каталоге"):
            catalogs_object_info = DiagramShortInfoView.construct(
                **get_offers_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Шаблон найден в каталоге"):
            assert catalogs_object_info.versionId == offer_without_catalog.versionId
