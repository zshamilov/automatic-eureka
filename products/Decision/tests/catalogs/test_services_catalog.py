import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import ResponseDto, ExternalServiceCatalogShortInfoDto, CatalogCreate, \
    ExternalServiceFullViewDto
from products.Decision.framework.steps.decision_steps_catalog import get_services_catalog_content_by_id, create_catalog, \
    delete_catalogs, find_service_in_services_catalogs, move_element_in_catalog
from products.Decision.framework.steps.decision_steps_external_service_api import delete_service, find_service_by_id


@allure.epic("Каталоги")
@allure.feature("Каталоги. Внешние сервисы")
@pytest.mark.scenario("DEV-7849")
class TestCatalogServices:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать сервис в каталоге, найти")
    @pytest.mark.smoke
    def test_create_service_in_catalog(self, super_user, created_catalog_id,
                                       create_service_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание сервиса в каталоге"):
            service_in_catalog: ResponseDto = create_service_gen.create_fake_valid_service(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объекте в каталоге"):
            catalogs_object_info = ExternalServiceCatalogShortInfoDto.construct(
                **get_services_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Сервис найден в каталоге"):
            assert catalogs_object_info.versionId == service_in_catalog.uuid

    @allure.story("Объект возможно удалить из каталога")
    @allure.title("Удалить сервис из каталога, проверить, что каталог пуст")
    @pytest.mark.smoke
    def test_delete_service_from_catalog(self, super_user, created_catalog_id,
                                         create_service_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание сервиса в каталоге"):
            service_in_catalog: ResponseDto = create_service_gen.create_fake_valid_service(
                catalog_id=catalog_id)
        with allure.step("Удаление сервиса в каталоге"):
            delete_service(super_user, service_in_catalog.uuid)
        with allure.step("Получение информации об объектах в каталоге"):
            catalogs_content = get_services_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Объектов в каталоге не обнаружено"):
            assert catalogs_content.status == 204

    @allure.story("При удалении каталога, объекты внутри него удаляются")
    @allure.title("Удалить каталог внутри которого находится сервис, сервис удалён")
    @pytest.mark.smoke
    def test_delete_catalog_service_in_catalog_deleted(self, super_user,
                                                       create_service_gen):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name)).body)
            catalog_id = str(create_resp.uuid)
        with allure.step("Создание сервиса в каталоге"):
            service_in_catalog: ResponseDto = create_service_gen.create_fake_valid_service(
                catalog_id=catalog_id)
        with allure.step("Удаление созданного каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Поиск сервиса"):
            found_service = find_service_in_services_catalogs(super_user, service_in_catalog.uuid)
        with allure.step("Сервис не найден"):
            assert found_service is None

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и сервис в каталоге, увидеть, что в каталоге сервисов только сервис")
    def test_only_services_in_service_catalog(self, super_user, created_catalog_id,
                                              create_service_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение сервиса в каталоге"):
            service_in_catalog: ResponseDto = create_service_gen.create_fake_valid_service(
                catalog_id=catalog_id)
        with allure.step("Сохранение диаграммы в каталоге"):
            save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге сервисов"):
            catalogs_objects_info = get_services_catalog_content_by_id(
                super_user, catalog_id).body["content"]
        with allure.step("В каталоге только один объект и это сервис"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["versionId"] == service_in_catalog.uuid for el in catalogs_objects_info)

    @allure.story("Сервис без каталога возможно поместить в каталог")
    @allure.title("Создать сервис и каталог, поместить сервис в каталог")
    @pytest.mark.smoke
    def test_service_in_catalog_move(self, super_user, created_catalog_id,
                                     create_service_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение сервиса без каталога"):
            service_without_catalog: ResponseDto = create_service_gen.create_fake_valid_service()
            service_version_id = service_without_catalog.uuid
            service_info: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, service_version_id).body
                ))
        with allure.step("Поиск сервиса в списке каталогов сервисов"):
            service_element_id = find_service_in_services_catalogs(
                super_user, service_version_id, service_name=service_info.objectName).elementId
        with allure.step("Перемещение сервиса в созданный каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id,
                                    element_id=service_element_id)
        with allure.step("Получение информации о первом объекте в созданном каталоге"):
            catalogs_object_info = ExternalServiceCatalogShortInfoDto.construct(
                **get_services_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Сервис найден в каталоге"):
            assert catalogs_object_info.versionId == service_without_catalog.uuid

    @allure.story("Сервис в каталоге возможно переместить в другой каталог")
    @allure.title("Создать два каталога и сервис внутри первого, переместить сервис из первого во второй каталог")
    @pytest.mark.smoke
    def test_service_in_catalog_move_in_another_cat(self, super_user, created_two_catalogs,
                                                    create_service_gen):
        catalog_id1 = created_two_catalogs["catalog_id1"]
        catalog_id2 = created_two_catalogs["catalog_id2"]
        with allure.step("Сохранение сервиса в первом каталоге"):
            service_in_catalog1: ResponseDto = create_service_gen.create_fake_valid_service(
                catalog_id=catalog_id1)
            service_version_id = service_in_catalog1.uuid
        with allure.step("Поиск сервиса в первом каталоге сервисов"):
            service_element_id = find_service_in_services_catalogs(super_user, service_version_id,
                                                                   catalog_id=catalog_id1).elementId
        with allure.step("Перемещение сервиса во второй каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id2,
                                    element_id=service_element_id)
        with allure.step("Получение информации о первом объекте во втором каталоге"):
            second_catalogs_object_info = ExternalServiceCatalogShortInfoDto.construct(
                **get_services_catalog_content_by_id(super_user, catalog_id2).body["content"][0])
        with allure.step("Получение информации о контенте в первом каталоге"):
            first_catalog_content = get_services_catalog_content_by_id(
                super_user, catalog_id1)
        with allure.step("Сервис найден во втором каталоге, первый каталог пуст"):
            assert second_catalogs_object_info.versionId == service_in_catalog1.uuid and \
                   first_catalog_content.status == 204
