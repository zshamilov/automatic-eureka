import allure
import pytest

from products.Decision.framework.model import ScriptCatalogShortInfoDto, ScriptFullView, DiagramViewDto
from products.Decision.framework.steps.decision_steps_catalog import get_scripts_catalog_content_by_id
from products.Decision.framework.steps.decision_steps_script_api import delete_script_by_id


@allure.epic("Каталоги")
@allure.feature("Каталоги. Кастомные коды")
@pytest.mark.scenario("DEV-7849")
class TestCatalogScripts:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать скрипт в каталоге, найти")
    @pytest.mark.smoke
    def test_create_script_in_catalog(self, super_user, created_catalog_id,
                                      create_code_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание скрипта в каталоге"):
            script_in_catalog: ScriptFullView = create_code_gen.create_p_code_in_catalog(
                catalog_id=catalog_id)["script_info"]
        with allure.step("Получение информации об объекте в каталоге"):
            catalogs_object_info = ScriptCatalogShortInfoDto.construct(
                **get_scripts_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Скрипт найден в каталоге"):
            assert catalogs_object_info.scriptId == script_in_catalog.scriptId and \
                   catalogs_object_info.objectName == script_in_catalog.objectName

    @allure.story("Объект возможно удалить из каталога")
    @allure.title("Удалить скрипт из каталога, проверить, что каталог пуст")
    @pytest.mark.smoke
    def test_delete_script_from_catalog(self, super_user, created_catalog_id,
                                        create_code_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание скрипта в каталоге"):
            script_in_catalog: ScriptFullView = create_code_gen.create_p_code_in_catalog(
                catalog_id=catalog_id)["script_info"]
        with allure.step("Удаление скрипта в каталоге"):
            delete_script_by_id(super_user, script_in_catalog.versionId)
        with allure.step("Получение информации об объектах в каталоге"):
            catalogs_content = get_scripts_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Объектов в каталоге не обнаружено"):
            assert catalogs_content.status == 204

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и скрипт в каталоге, увидеть, что в каталоге скриптов только скрипт")
    @pytest.mark.smoke
    def test_only_scripts_in_script_catalog(self, super_user, created_catalog_id,
                                            create_code_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение скрипта в каталоге"):
            script_in_catalog: ScriptFullView = create_code_gen.create_p_code_in_catalog(
                catalog_id=catalog_id)["script_info"]
        with allure.step("Сохранение диаграммы в каталоге"):
            save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге скриптов"):
            catalogs_objects_info = get_scripts_catalog_content_by_id(
                super_user, catalog_id).body["content"]
        with allure.step("В каталоге только один объект и это скрипт"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["scriptId"] == script_in_catalog.scriptId for el in catalogs_objects_info)
