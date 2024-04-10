import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import CatalogPage
from products.Decision.framework.steps.decision_steps_catalog import get_all_catalogs, \
    get_diagrams_catalog_content_by_id


@allure.epic("Каталоги")
@allure.feature("Создание каталога")
@pytest.mark.scenario("DEV-7849")
class TestCatalogCreate:

    @allure.story("Созданный каталог появляется в списке каталогов")
    @allure.title("Создать каталог, найти в списке")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_create_catalog(self, super_user,
                            create_catalogs_gen):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            catalog_id: str = create_catalogs_gen.create_catalog(
                catalog_name=catalog_name)
        with allure.step("Получение списка каталогов"):
            found_catalogs = CatalogPage(
                **get_all_catalogs(super_user).body).content
        with allure.step("Созданный каталог найден в списке каталогов"):
            assert any(str(cat.catalogId) == catalog_id for cat in found_catalogs)

    @allure.story("Длина имени каталога не должна превышать 100 символов")
    @allure.title("Создаем каталог, проверяем длину имени")
    @pytest.mark.parametrize("name_length, status_code", [(99, 201),
                                                          (100, 201)])
    @pytest.mark.sdi
    def test_create_catalog_name_length(self, super_user,
                                        create_catalogs_gen,
                                        name_length, status_code):
        with allure.step("Создание каталога"):
            catalog_name = generate_string(name_length)
            create_response = create_catalogs_gen.try_create_catalog(
                catalog_name=catalog_name)
        with allure.step("Недопустимо название каталога с длиной более 100 символов"):
            assert create_response.status == status_code

    @allure.story("Длина имени каталога не должна превышать 100 символов")
    @allure.title("Создаем каталог, проверяем длину имени")
    @pytest.mark.parametrize("name_length, status_code", [(101, 400)])
    @pytest.mark.sdi
    def test_create_catalog_name_length_neg(self, super_user,
                                            create_catalogs_gen,
                                            name_length, status_code):
        with allure.step("Создание каталога"):
            catalog_name = generate_string(name_length)
        with allure.step("Недопустимо название каталога с длиной более 100 символов"):
            with pytest.raises(HTTPError, match=str(status_code)):
                assert create_catalogs_gen.try_create_catalog(
                    catalog_name=catalog_name).status == status_code

    @allure.story("Можно создать каталог в каталоге")
    @allure.title("Создать родительский каталог, создать каталог, сохранить в родительский")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_create_catalog_in_catalog(self, super_user,
                                       create_catalogs_gen):
        with allure.step("Создание родительского каталога"):
            catalog_name_parent = "ag_test_catalog_" + generate_string()
            catalog_id_parent: str = create_catalogs_gen.create_catalog(
                catalog_name=catalog_name_parent)
        with allure.step("Создание каталога в родительском каталоге"):
            catalog_name = "ag_test_catalog_" + generate_string()
            catalog_id: str = create_catalogs_gen.create_catalog(
                catalog_name=catalog_name, parent_catalog_id=catalog_id_parent)
        with allure.step("Поиск каталога в родительском каталоге"):
            catalog_content = get_diagrams_catalog_content_by_id(
                super_user, catalog_id_parent).body["content"]
        with allure.step("Созданный каталог найден в списке каталогов"):
            assert any(cat["catalogId"] == catalog_id and cat["catalogFlag"]
                       for cat in catalog_content)
