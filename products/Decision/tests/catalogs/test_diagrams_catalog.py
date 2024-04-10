import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import DiagramCatalogShortInfoView, DiagramInOutParametersViewDto, \
    ScriptFullView, DiagramViewDto
from products.Decision.framework.steps.decision_steps_catalog import get_diagrams_catalog_content_by_id
from products.Decision.framework.steps.decision_steps_diagram import delete_diagram


@allure.epic("Каталоги")
@allure.feature("Каталоги. Диаграммы")
@pytest.mark.scenario("DEV-7849")
class TestCatalogDiagrams:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать диаграмму в каталоге и сохранить, найти")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_create_diagram_in_catalog(self, super_user, created_catalog_id,
                                       create_temp_diagram_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание шаблона диаграммы в каталоге"):
            template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template(
                catalog_id=catalog_id)
        with allure.step("Сохранение диаграммы в каталоге"):
            saved_diagram_name = "ag_diag_for_cat_" + generate_string()
            diagram_description = "diagram created in test"
            create_result = save_diagrams_gen.save_diagram(
                template.diagramId, template.versionId,
                saved_diagram_name, diagram_description
            ).body
            saved_version_id = create_result["uuid"]
        with allure.step("Получение информации о созданном каталоге диаграмм"):
            catalogs_object_info = DiagramCatalogShortInfoView.construct(
                **get_diagrams_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Диаграмма найдена в данном каталоге"):
            assert catalogs_object_info.versionId == saved_version_id and \
                   catalogs_object_info.objectName == saved_diagram_name

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и скрипт в каталоге, увидеть, что в каталоге диаграмм только диаграмма")
    def test_only_diagrams_are_in_catalog(self, super_user, created_catalog_id,
                                          create_code_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание скрипта в каталоге"):
            script_in_catalog: ScriptFullView = create_code_gen.create_p_code_in_catalog(
                catalog_id=catalog_id)["script_info"]
        with allure.step("Сохранение диаграммы в каталоге"):
            diagram_in_catalog: DiagramViewDto = save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге диаграмм"):
            catalogs_objects_info = get_diagrams_catalog_content_by_id(
                super_user, catalog_id).body["content"]
        with allure.step("Внутри каталога только один объект и это диаграмма"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["versionId"] == str(diagram_in_catalog.versionId)
                       for el in catalogs_objects_info)

    @allure.story("Удалённая диаграмма пропадает из каталога")
    @allure.title("Удалить диаграмму из каталога, проверить, что каталог пуст")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_diagram_from_catalog(self, super_user, created_catalog_id,
                                         create_temp_diagram_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание шаблона диаграммы в каталоге"):
            template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template(
                catalog_id=catalog_id)
        with allure.step("Сохранение диаграммы в каталоге"):
            saved_diagram_name = "ag_diag_for_cat_" + generate_string()
            diagram_description = "diagram created in test"
            create_result = save_diagrams_gen.save_diagram(
                template.diagramId, template.versionId,
                saved_diagram_name, diagram_description
            ).body
            saved_version_id = create_result["uuid"]
        with allure.step("Удаление диаграммы из каталога"):
            delete_diagram(super_user, saved_version_id)
        with allure.step("Получение информации о созданном каталоге диаграмм"):
            catalog_objects_info = get_diagrams_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Удалённая диаграмма не найдена в каталоге"):
            assert catalog_objects_info.status == 204

    @allure.story("Только latest версия диаграммы отображается в каталоге")
    @allure.title("Создать шаблон в каталоге, увидитеть, что каталог пуст")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_only_latest_in_catalog(self, super_user, created_catalog_id,
                                    create_temp_diagram_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание шаблона диаграммы в каталоге"):
            create_temp_diagram_gen.create_template(catalog_id=catalog_id)
        with allure.step("Получение информации о созданном каталоге диаграмм"):
            catalog_objects_info = get_diagrams_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Шаблон диаграммы в каталоге не отображается"):
            assert catalog_objects_info.status == 204
