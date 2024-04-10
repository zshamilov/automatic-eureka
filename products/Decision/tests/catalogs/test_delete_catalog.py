import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import CatalogCreate, ResponseDto, CatalogPage
from products.Decision.framework.steps.decision_steps_catalog import create_catalog, delete_catalogs, get_all_catalogs


@allure.epic("Каталоги")
@allure.feature("Удаление каталога")
@pytest.mark.scenario("DEV-7849")
class TestCatalogDelete:

    @allure.story("Удалённый каталог пропадает из списка каталогов")
    @allure.title("Удалить созданный каталог, проверить, что пропал из списка")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_catalog(self, super_user):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name)).body)
            catalog_id = str(create_resp.uuid)
        with allure.step("Удаление созданного каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Получение списка каталогов"):
            found_catalogs = CatalogPage(
                **get_all_catalogs(super_user).body).content
        with allure.step("Удалённый каталог не найден в списке каталогов"):
            assert not any(cat.catalogId == catalog_id for cat in found_catalogs)

    @allure.story("При удалении родительского каталога удаляются все внутренние")
    @allure.title("Создать каталог внутри другого, удалить внешний")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_parent_catalog(self, super_user):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name)).body)
            catalog_id = create_resp.uuid
        with allure.step("Создание каталога внутри созданного"):
            inner_catalog_name = "ag_inner_catalog_" + generate_string()
            inner_create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=inner_catalog_name,
                    parentCatalogId=catalog_id)).body)
            inner_catalog_id = str(inner_create_resp.uuid)
        with allure.step("Удаление внешнего каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Получение списка каталогов"):
            found_catalogs = CatalogPage(
                **get_all_catalogs(super_user).body).content
        with allure.step("Ни внешний, ни внутренний каталоги не найдены"):
            assert not any(cat.catalogId == str(catalog_id) or
                           cat.catalogId == inner_catalog_id for cat in found_catalogs)
