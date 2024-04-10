import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import UserFunctionShortInfo, UserFunctionCatalogShortInfo, ResponseDto, \
    CatalogCreate
from products.Decision.framework.steps.decision_steps_catalog import get_funcs_catalog_content_by_id, create_catalog, \
    delete_catalogs, find_func_in_funcs_catalogs, move_element_in_catalog
from products.Decision.framework.steps.decision_steps_user_functions import delete_user_functions


@allure.epic("Каталоги")
@allure.feature("Каталоги. Пользовательские функции")
@pytest.mark.scenario("DEV-7849")
class TestCatalogUFuncs:

    @allure.story("Объект сохраняется в выбранный каталог")
    @allure.title("Создать пользовательскую функцию в каталоге, найти")
    @pytest.mark.smoke
    def test_create_func_in_catalog(self, super_user, created_catalog_id,
                                    upload_funcs_gen):
        catalog_id = created_catalog_id
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2",
                catalog_id=catalog_id
            )
        with allure.step("Получение информации об объекте в каталоге"):
            catalogs_object_info = UserFunctionCatalogShortInfo.construct(
                **get_funcs_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Пользовательский тип найден в каталоге"):
            assert catalogs_object_info.id == user_func.id and \
                   catalogs_object_info.objectName == user_func.objectName

    @allure.story("Объект возможно удалить из каталога")
    @allure.title("Удалить пользовательскую функцию из каталога, проверить, что каталог пуст")
    @pytest.mark.smoke
    def test_delete_func_in_catalog(self, super_user, created_catalog_id,
                                    upload_funcs_gen):
        catalog_id = created_catalog_id
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2",
                catalog_id=catalog_id
            )
        with allure.step("Удаление пользовательского типа в каталоге"):
            delete_user_functions(super_user, func_ids=[str(user_func.id)])
        with allure.step("Получение информации об объектах в каталоге"):
            catalogs_content = get_funcs_catalog_content_by_id(super_user, catalog_id)
        with allure.step("Объектов в каталоге не обнаружено"):
            assert catalogs_content.status == 204

    @allure.story("При удалении каталога, объекты внутри него удаляются")
    @allure.title("Удалить каталог внутри которого находится функция, функция удалёна")
    @pytest.mark.smoke
    def test_delete_catalog_func_in_catalog_deleted(self, super_user,
                                                    upload_funcs_gen):
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name)).body)
            catalog_id = str(create_resp.uuid)
        with allure.step("Добавление пользовательской функции"):
            user_func_in_cat: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2",
                catalog_id=catalog_id
            )
        with allure.step("Удаление созданного каталога"):
            delete_catalogs(super_user, catalog_ids=[catalog_id])
        with allure.step("Поиск пользовательской функции"):
            found_func = find_func_in_funcs_catalogs(super_user, user_func_in_cat.id,
                                                     func_name=user_func_in_cat.objectName)
        with allure.step("Функция не найдена"):
            assert found_func is None

    @allure.story("В каталоге отображаются только объекты одного типа в зависимости от раздела")
    @allure.title("Создать диаграмму и пользовательскую функцию в каталоге, увидеть, что в каталоге функций только "
                  "функция")
    def test_func_in_catalog_only_func(self, super_user, created_catalog_id,
                                       upload_funcs_gen, save_diagrams_gen):
        catalog_id = created_catalog_id
        with allure.step("Добавление пользовательской функции в каталоге"):
            user_func_in_cat: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2",
                catalog_id=catalog_id
            )
        with allure.step("Сохранение диаграммы в том же каталоге"):
            save_diagrams_gen.save_empty_diagram_in_catalog(
                catalog_id=catalog_id)
        with allure.step("Получение информации об объектах в каталоге пользовательских функций"):
            catalogs_objects_info = get_funcs_catalog_content_by_id(
                super_user, catalog_id).body["content"]
        with allure.step("В каталоге только один объект и это функция"):
            assert len(catalogs_objects_info) == 1 and \
                   all(el["id"] == user_func_in_cat.id for el in catalogs_objects_info)

    @allure.story("Пользовательскую функцию без каталога возможно поместить в каталог")
    @allure.title("Создать функцию и каталог, поместить функцию в каталог")
    @pytest.mark.smoke
    def test_func_in_catalog_move(self, super_user, created_catalog_id,
                                  upload_funcs_gen):
        catalog_id = created_catalog_id
        with allure.step("Добавление пользовательской функции без каталога"):
            user_func_without_cat: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2"
            )
            func_id = user_func_without_cat.id
        with allure.step("Поиск функции в списке каталогов функций"):
            func_element_id = find_func_in_funcs_catalogs(
                super_user, func_id,
                func_name=user_func_without_cat.objectName).elementId
        with allure.step("Перемещение функции в созданный каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id,
                                    element_id=func_element_id)
        with allure.step("Получение информации о первом объекте в созданном каталоге"):
            catalogs_object_info = UserFunctionCatalogShortInfo.construct(
                **get_funcs_catalog_content_by_id(super_user, catalog_id).body["content"][0])
        with allure.step("Пользовательская функция найден в каталоге"):
            assert catalogs_object_info.id == user_func_without_cat.id and \
                   catalogs_object_info.objectName == user_func_without_cat.objectName

    @allure.story("Пользовательскую функцию в каталоге возможно переместить в другой каталог")
    @allure.title("Создать два каталога и функцию внутри первого, переместить функцию из первого во второй каталог")
    @pytest.mark.smoke
    def test_func_in_catalog_move_in_another_cat(self, super_user, created_two_catalogs,
                                                 upload_funcs_gen):
        catalog_id1 = created_two_catalogs["catalog_id1"]
        catalog_id2 = created_two_catalogs["catalog_id2"]
        with allure.step("Добавление пользовательской функции в первый каталог"):
            user_func_in_cat1: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2",
                catalog_id=catalog_id1
            )
        with allure.step("Поиск функции в первом каталоге"):
            func_element_id = find_func_in_funcs_catalogs(
                super_user, user_func_in_cat1.id,
                func_name=user_func_in_cat1.objectName).elementId
        with allure.step("Перемещение функции во второй каталог"):
            move_element_in_catalog(super_user,
                                    target_catalog_id=catalog_id2,
                                    element_id=func_element_id)
        with allure.step("Получение информации о первом объекте во втором каталоге"):
            second_catalogs_object_info = UserFunctionCatalogShortInfo.construct(
                **get_funcs_catalog_content_by_id(super_user, catalog_id2).body["content"][0])
        with allure.step("Получение информации о контенте в первом каталоге"):
            first_catalog_content = get_funcs_catalog_content_by_id(
                super_user, catalog_id1)
        with allure.step("Пользовательская функция найдена во втором каталоге, первый каталог пуст"):
            assert second_catalogs_object_info.id == user_func_in_cat1.id and \
                   second_catalogs_object_info.objectName == user_func_in_cat1.objectName and \
                   first_catalog_content.status == 204
