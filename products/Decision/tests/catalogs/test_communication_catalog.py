import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import CommunicationChannelFullViewDto, CommunicationChannelCatalogShortInfoDto, \
    ResponseDto, CatalogCreate
from products.Decision.framework.steps.decision_steps_catalog import create_catalog, delete_catalogs, \
    move_element_in_catalog
from products.Decision.framework.steps.decision_steps_communication_api import get_channel_catalog_content_by_id, \
    find_channel_in_channel_catalogs, delete_communication


@allure.epic("Каталоги")
@allure.feature("Каталоги. Каналы коммуникации")
@pytest.mark.scenario("DEV-7849")
class TestCatalogCommunication:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать канал в каталоге, найти")
    @pytest.mark.smoke
    def test_create_communication_in_catalog(self, super_user, created_catalog_id, create_communication_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание канала в каталоге"):
            channel_in_catalog: CommunicationChannelFullViewDto = create_communication_gen.create_channel_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объекте в каталоге"):
            catalogs_object_info = CommunicationChannelCatalogShortInfoDto.construct(
                **get_channel_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Канал коммуникации найден в каталоге"):
            assert catalogs_object_info.communicationChannelId == channel_in_catalog.communicationChannelId and \
                   catalogs_object_info.objectName == channel_in_catalog.objectName

    @allure.story("Объект возможно удалить из каталога")
    @allure.title("Удалить канал коммуникации из каталога, проверить, что каталог пуст")
    @pytest.mark.smoke
    def test_delete_communication_in_catalog(self, super_user, created_catalog_id, create_communication_gen):
        catalog_id = created_catalog_id
        with allure.step("Создание канала коммуникации в каталоге"):
            channel_in_catalog: CommunicationChannelFullViewDto = create_communication_gen.create_channel_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Удаление канала коммуникации в каталоге"):
            delete_communication(super_user, version_id=channel_in_catalog.versionId)
        with allure.step("Получение информации об объектах в каталоге"):
            catalogs_content = get_channel_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Объектов в каталоге не обнаружено"):
            assert catalogs_content.status == 204 and \
                   not catalogs_content.body

    @allure.story("При удалении каталога, объекты внутри него удаляются")
    @allure.title("Удалить каталог внутри которого находится канал, канал удалён")
    @pytest.mark.smoke
    def test_delete_catalog_communication_in_catalog_deleted(self, super_user,
                                                             create_communication_gen):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name)).body)
            catalog_id = str(create_resp.uuid)
        with allure.step("Создание агрегата в каталоге"):
            channel_in_catalog: CommunicationChannelFullViewDto = create_communication_gen.create_channel_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Удаление созданного каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Поиск канала"):
            found_channel = find_channel_in_channel_catalogs(super_user, channel_in_catalog.versionId,
                                                             channel_name=channel_in_catalog.objectName)
        with allure.step("канал не найден"):
            assert found_channel is None

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и канал в каталоге, увидеть, что в каталоге каналов только канал")
    def test_only_communication_in_catalog(self, super_user, created_catalog_id,
                                           create_communication_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение канал в каталоге"):
            channel_in_catalog: CommunicationChannelFullViewDto = create_communication_gen.create_channel_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Сохранение диаграммы в каталоге"):
            save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге каналов"):
            catalogs_objects_info = get_channel_catalog_content_by_id(super_user, catalog_id).body["content"]
        with allure.step("В каталоге только один объект и это канал"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["communicationChannelId"] == channel_in_catalog.communicationChannelId
                       for el in catalogs_objects_info)

    @allure.story("канал без каталога возможно поместить в каталог")
    @allure.title("Создать канал и каталог, поместить канал в каталог")
    @pytest.mark.smoke
    def test_communication_in_catalog_move(self, super_user, created_catalog_id,
                                           create_communication_gen):
        catalog_id = created_catalog_id
        with allure.step("Сохранение агрегата без каталога"):
            channel_without_catalog: CommunicationChannelFullViewDto = \
                create_communication_gen.create_channel_in_catalog(catalog_id=None)
            aggregate_version_id = channel_without_catalog.versionId
        with allure.step("Поиск канала в списке каталогов агрегатов"):
            channel_element_id = find_channel_in_channel_catalogs(
                super_user, aggregate_version_id,
                channel_name=channel_without_catalog.objectName).elementId
        with allure.step("Перемещение канала в созданный каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id,
                                    element_id=channel_element_id)
        with allure.step("Получение информации о первом объекте в созданном каталоге"):
            catalogs_object_info = CommunicationChannelCatalogShortInfoDto.construct(
                **get_channel_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("канал найден в каталоге"):
            assert catalogs_object_info.communicationChannelId == channel_without_catalog.communicationChannelId and \
                   catalogs_object_info.objectName == channel_without_catalog.objectName

    @allure.story("Канал в каталоге возможно переместить в другой каталог")
    @allure.title("Создать два каталога и канал внутри первого, переместить канал из первого во второй каталог")
    @pytest.mark.smoke
    def test_communication_in_catalog_move_in_another_cat(self, super_user, created_two_catalogs,
                                                          create_communication_gen):
        catalog_id1 = created_two_catalogs["catalog_id1"]
        catalog_id2 = created_two_catalogs["catalog_id2"]
        with allure.step("Сохранение канала в первом каталоге"):
            channel_in_catalog1: CommunicationChannelFullViewDto = create_communication_gen.create_channel_in_catalog(
                catalog_id=catalog_id1)
            channel_version_id = channel_in_catalog1.versionId
        with allure.step("Поиск канала в первом каталоге каналов"):
            channel_element_id = find_channel_in_channel_catalogs(super_user, channel_version_id,
                                                                  catalog_id=catalog_id1).elementId
        with allure.step("Перемещение канала во второй каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id2,
                                    element_id=channel_element_id)
        with allure.step("Получение информации о первом объекте во втором каталоге"):
            second_catalogs_object_info = CommunicationChannelCatalogShortInfoDto.construct(
                **get_channel_catalog_content_by_id(super_user, catalog_id2).body["content"][0])
        with allure.step("Получение информации о контенте в первом каталоге"):
            first_catalog_content = get_channel_catalog_content_by_id(
                super_user, catalog_id1)
        with allure.step("канал найден во втором каталоге, первый каталог пуст"):
            assert second_catalogs_object_info.communicationChannelId == channel_in_catalog1.communicationChannelId and \
                   second_catalogs_object_info.objectName == channel_in_catalog1.objectName and \
                   first_catalog_content.status == 204
