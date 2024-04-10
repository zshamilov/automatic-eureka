import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import CatalogPage, CatalogShortView, DiagramCatalogShortInfoView
from products.Decision.framework.steps.decision_steps_catalog import update_catalog, get_catalog_by_name, \
    get_diagrams_catalog_content_by_id, find_catalog_in_diagram_catalog_by_id, move_element_in_catalog


@allure.epic("Каталоги")
@allure.feature("Изменение каталога")
@pytest.mark.scenario("DEV-7849")
class TestCatalogUpdate:

    @allure.story("Каталогу возможно изменить имя")
    @allure.title("Изменить имя каталога, проверить, что id прежний, а имя сменилось")
    @pytest.mark.parametrize("name_length", [99, 100])
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_change_catalog_name(self, super_user,
                                 create_catalogs_gen, name_length):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            catalog_id: str = create_catalogs_gen.create_catalog(
                catalog_name=catalog_name)
        with allure.step("Обновление имени каталога"):
            updated_name = generate_string(name_length)
            update_catalog(super_user, updated_name, catalog_id)
        with allure.step("Поиск каталога в списке"):
            catalog_info: CatalogShortView = CatalogPage(
                **get_catalog_by_name(
                    super_user, catalog_name=updated_name).body).content[0]
        with allure.step("Имя каталога обновлено, а идентификатор остался прежним"):
            assert str(catalog_info.catalogId) == catalog_id and \
                   catalog_info.catalogName == updated_name

    @allure.story("Каталог возможно переместить в другой каталог")
    @allure.title("Создать два каталога, переместить один в другой")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_change_catalog_move(self, super_user,
                                 create_catalogs_gen):
        with allure.step("Создание каталога 1"):
            catalog_name1 = "ag_test_catalog1_" + generate_string()
            catalog_id1: str = create_catalogs_gen.create_catalog(
                catalog_name=catalog_name1)
        with allure.step("Создание каталога 2"):
            catalog_name2 = "ag_test_catalog2_" + generate_string()
            catalog_id2: str = create_catalogs_gen.create_catalog(
                catalog_name=catalog_name2)
            catalog1: DiagramCatalogShortInfoView = find_catalog_in_diagram_catalog_by_id(super_user, catalog_id1)
            catalog2: DiagramCatalogShortInfoView = find_catalog_in_diagram_catalog_by_id(super_user, catalog_id2)
        with allure.step("Перемещение каталога в другой каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog1.catalogId,
                                    element_id=catalog2.elementId)
            catalog1_inner_info = DiagramCatalogShortInfoView.construct(
                **get_diagrams_catalog_content_by_id(super_user, catalog_id1).body["content"][0])
            assert catalog1_inner_info.objectName == catalog_name2 and \
                   catalog1_inner_info.catalogId == catalog_id2

    @allure.story("Имя каталога при изменении не должно превышать 100 символов")
    @allure.title(
        "Изменить имя каталога на больше 100 символов, проверить, что имя не изменилось, каталог с таким названием не "
        "существует")
    @pytest.mark.sdi
    def test_change_catalog_name_length_neg(self, super_user,
                                            create_catalogs_gen):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            catalog_id: str = create_catalogs_gen.create_catalog(
                catalog_name=catalog_name)
        with allure.step("Обновление имени каталога"):
            updated_name = generate_string(101)
        with allure.step("Обновления имени каталога не произошло"):
            with pytest.raises(HTTPError):
                assert update_catalog(super_user, updated_name, catalog_id).status == 400
