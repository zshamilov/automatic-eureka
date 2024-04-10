import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import ComplexTypeGetFullView, ComplexTypeCatalogShortView, ResponseDto, \
    CatalogCreate
from products.Decision.framework.steps.decision_steps_catalog import get_types_catalog_content_by_id, \
    find_type_in_types_catalogs, move_element_in_catalog, create_catalog, delete_catalogs
from products.Decision.framework.steps.decision_steps_complex_type import delete_custom_type


@allure.epic("Каталоги")
@allure.feature("Каталоги. Пользовательские типы данных")
@pytest.mark.scenario("DEV-7849")
class TestCatalogCTypes:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать пользовательский тип в каталоге, найти")
    @pytest.mark.smoke
    def test_create_type_in_catalog(self, super_user, created_catalog_id,
                                    create_custom_types_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание пользовательского типа в каталоге"):
            type_in_catalog: ComplexTypeGetFullView = create_custom_types_gen.create_type_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объекте в каталоге"):
            catalogs_object_info = ComplexTypeCatalogShortView.construct(
                **get_types_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Пользовательский тип найден в каталоге"):
            assert catalogs_object_info.typeId == type_in_catalog.typeId and \
                   catalogs_object_info.objectName == type_in_catalog.objectName

    @allure.story("Объект возможно удалить из каталога")
    @allure.title("Удалить пользовательский тип из каталога, проверить, что каталог пуст")
    @pytest.mark.smoke
    def test_delete_type_in_catalog(self, super_user, created_catalog_id,
                                    create_custom_types_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание пользовательского типа в каталоге"):
            type_in_catalog: ComplexTypeGetFullView = create_custom_types_gen.create_type_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Удаление пользовательского типа в каталоге"):
            delete_custom_type(super_user, str(type_in_catalog.versionId))
        with allure.step("Получение информации об объектах в каталоге"):
            catalogs_content = get_types_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Объектов в каталоге не обнаружено"):
            assert catalogs_content.status == 204

    @allure.story("При удалении каталога, объекты внутри него удаляются")
    @allure.title("Удалить каталог внутри которого находится тип, тип удалён")
    @pytest.mark.smoke
    def test_delete_catalog_type_in_catalog_deleted(self, super_user,
                                                    create_custom_types_gen):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name)).body)
            catalog_id = str(create_resp.uuid)
        with allure.step("Создание пользовательского типа в каталоге"):
            type_in_catalog: ComplexTypeGetFullView = create_custom_types_gen.create_type_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Удаление созданного каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Поиск пользовательского типа"):
            found_type = find_type_in_types_catalogs(super_user, type_in_catalog.versionId,
                                                     type_name=type_in_catalog.objectName)
        with allure.step("Тип не найден"):
            assert found_type is None

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и пользовательский тип в каталоге, увидеть, что в каталоге типов только тип")
    def test_type_in_catalog_only_type(self, super_user, created_catalog_id,
                                       create_custom_types_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение пользовательского типа в каталоге"):
            type_in_catalog: ComplexTypeGetFullView = create_custom_types_gen.create_type_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Сохранение диаграммы в каталоге"):
            save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге пользовательских типа"):
            catalogs_objects_info = get_types_catalog_content_by_id(
                super_user, catalog_id).body["content"]
        with allure.step("В каталоге только один объект и это пользовательский тип"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["typeId"] == type_in_catalog.typeId for el in catalogs_objects_info)

    @allure.story("Пользовательский тип без каталога возможно поместить в каталог")
    @allure.title("Создать тип и каталог, поместить тип в каталог")
    @pytest.mark.smoke
    def test_type_in_catalog_move(self, super_user, created_catalog_id,
                                  create_custom_types_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение пользовательского типа без каталога"):
            type_without_catalog: ComplexTypeGetFullView = create_custom_types_gen.create_type_in_catalog(
                catalog_id=None)
            type_version_id = type_without_catalog.versionId
        with allure.step("Поиск типа в списке каталогов пользовательских типов"):
            type_element_id = find_type_in_types_catalogs(super_user, type_version_id,
                                                          type_name=type_without_catalog.objectName).elementId
        with allure.step("Перемещение типа в созданный каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id,
                                    element_id=type_element_id)
        with allure.step("Получение информации о первом объекте в созданном каталоге"):
            catalogs_object_info = ComplexTypeCatalogShortView.construct(
                **get_types_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Пользовательский тип найден в каталоге"):
            assert catalogs_object_info.typeId == type_without_catalog.typeId and \
                   catalogs_object_info.objectName == type_without_catalog.objectName

    @allure.story("Пользовательский тип в каталоге возможно переместить в другой каталог")
    @allure.title("Создать два каталога и тип внутри первого, переместить тип из первого во второй каталог")
    @pytest.mark.smoke
    def test_type_in_catalog_move_in_another_cat(self, super_user, created_two_catalogs,
                                                 create_custom_types_gen):
        catalog_id1 = created_two_catalogs["catalog_id1"]
        catalog_id2 = created_two_catalogs["catalog_id2"]
        with allure.step("Сохранение пользовательского типа в первом каталоге"):
            type_in_catalog1: ComplexTypeGetFullView = create_custom_types_gen.create_type_in_catalog(
                catalog_id=catalog_id1)
            type_version_id = type_in_catalog1.versionId
        with allure.step("Поиск типа в первом каталоге пользовательских типов"):
            type_element_id = find_type_in_types_catalogs(super_user, type_version_id,
                                                          catalog_id=catalog_id1).elementId
        with allure.step("Перемещение типа во второй каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id2,
                                    element_id=type_element_id)
        with allure.step("Получение информации о первом объекте во втором каталоге"):
            second_catalogs_object_info = ComplexTypeCatalogShortView.construct(
                **get_types_catalog_content_by_id(super_user, catalog_id2).body["content"][0])
        with allure.step("Получение информации о контенте в первом каталоге"):
            first_catalog_content = get_types_catalog_content_by_id(
                super_user, catalog_id1)
        with allure.step("Пользовательский тип найден во втором каталоге, первый каталог пуст"):
            assert second_catalogs_object_info.typeId == type_in_catalog1.typeId and \
                   second_catalogs_object_info.objectName == type_in_catalog1.objectName and \
                   first_catalog_content.status == 204
