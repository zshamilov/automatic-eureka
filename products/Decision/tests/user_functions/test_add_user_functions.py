import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import UserJarFunctionsDto, UserJarFullViewDto, UserFunctionShortView, \
    UserFunctionUploadView, UserFunctionShortInfo
from products.Decision.framework.steps.decision_steps_user_functions import get_jar_files_list, get_functions_list


@allure.epic("Настройка функций")
@allure.feature("Добавление пользовательской функции")
@pytest.mark.scenario("DEV-6110")
class TestUserFuncsCreate:

    @allure.story("Jar файл добавляется в систему")
    @allure.title("Загрузить jar-file в систему, проверить, что найден")
    @allure.link("DEV-6110")
    @pytest.mark.smoke
    def test_upload_jar_file(self, super_user, upload_funcs_gen):
        with allure.step("Загрузка jar файл в систему"):
            upload_response: UserJarFunctionsDto = upload_funcs_gen.upload_jar_file(
                file="products/Decision/resources/user_funcs_testing.jar")
            jar_id = upload_response.jarId
        with allure.step("Получение списка jar файлов"):
            files = []
            for file in get_jar_files_list(super_user).body:
                files.append(UserJarFullViewDto.construct(**file))
        with allure.step("Проверка, что загруженный файл найден"):
            assert any(file.id == jar_id for file in files)

    @allure.story("Из файла возможно выгрузить пользовательскую функцию")
    @allure.title("Загрузить функцию из файла, проверить, что появилась")
    @allure.link("DEV-6110")
    @pytest.mark.smoke
    def test_add_user_func_from_file(self, super_user, upload_funcs_gen):
        function_found = False
        with allure.step("Загрузка jar файл в систему"):
            upload_response: UserJarFunctionsDto = upload_funcs_gen.upload_jar_file(
                file="products/Decision/resources/user_funcs_testing.jar")
            jar_id = upload_response.jarId
            functions = upload_response.functions
            add_int_to_str: UserFunctionShortView = UserFunctionShortView.construct()
            for f in functions:
                if f.objectName == "returnString(java.lang.Integer)":
                    add_int_to_str = f
        with allure.step("Загрузка пользовательской функции из файла"):
            func_description = "made_in_test_" + generate_string()
            func_body = UserFunctionUploadView(objectName=add_int_to_str.objectName,
                                               jarFunctionName=add_int_to_str.jarFunctionName,
                                               functionClass=add_int_to_str.functionClass,
                                               resultType="2",
                                               description=func_description)
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func(jar_id, functions_body=[func_body])
        with allure.step("Получение списка функций"):
            function_list = []
            for f in get_functions_list(super_user).body["content"]:
                function_list.append(UserFunctionShortInfo.construct(**f))
            for f in function_list:
                if f.id == user_func.id:
                    function_found = True
        with allure.step("Проверка, что загруженная функция найдена"):
            assert function_found

    @allure.story("Недопустимо загружать функцию с параметрами, несоответствующими jar-файлу,"
                  " из которого они загружены")
    @allure.title("Задать некорректное имя, проверить, что сохранения не произошло")
    @pytest.mark.parametrize("name_bad", ["returnString(incorrect1, incorrect2)",
                                          "oh_that's_very_wrong_name(java.lang.Integer)"])
    def test_add_user_func_from_file_wrong_jar_params(self, super_user, upload_funcs_gen, name_bad):
        with allure.step("Загрузка jar файл в систему"):
            upload_response: UserJarFunctionsDto = upload_funcs_gen.upload_jar_file(
                file="products/Decision/resources/user_funcs_testing.jar")
            jar_id = upload_response.jarId
            functions = upload_response.functions
            add_int_to_str: UserFunctionShortView = UserFunctionShortView.construct()
            for f in functions:
                if f.objectName == "returnString(java.lang.Integer)":
                    add_int_to_str = f
        with allure.step("Загрузка пользовательской функции из файла"):
            func_description = "made_in_test_" + generate_string()
            func_body = UserFunctionUploadView(objectName=name_bad,  # wrong names go here
                                               jarFunctionName=add_int_to_str.jarFunctionName,
                                               functionClass=add_int_to_str.functionClass,
                                               resultType="2",
                                               description=func_description)
        with allure.step("Проверка, что не удалось загрузить пользовательскую функцию с некорректным названием"):
            with pytest.raises(HTTPError, match="400"):
                assert upload_funcs_gen.try_add_user_func(jar_id, functions_body=[func_body]).status\
                       == 400

    @allure.story("Недопустимо загружать функцию с параметрами, несоответствующими jar-файлу,"
                  " из которого они загружены")
    @allure.title("Задать некорректное jarFunctionName, проверить, что сохранения не произошло")
    def test_add_user_func_from_file_wrong_jar_func_name(self, super_user, upload_funcs_gen):
        with allure.step("Загрузка jar файл в систему"):
            upload_response: UserJarFunctionsDto = upload_funcs_gen.upload_jar_file(
                file="products/Decision/resources/user_funcs_testing.jar")
            jar_id = upload_response.jarId
            functions = upload_response.functions
            add_int_to_str: UserFunctionShortView = UserFunctionShortView.construct()
            for f in functions:
                if f.objectName == "returnString(java.lang.Integer)":
                    add_int_to_str = f
        with allure.step("Загрузка пользовательской функции из файла"):
            func_description = "made_in_test_" + generate_string()
            func_body = UserFunctionUploadView(objectName=add_int_to_str.objectName,
                                               jarFunctionName="not a jar file name",
                                               functionClass=add_int_to_str.functionClass,
                                               resultType="2",
                                               description=func_description)
        with allure.step("Проверка, что не удалось загрузить пользовательскую функцию с некорректным jarFunctionNameм"):
            with pytest.raises(HTTPError, match="400"):
                assert upload_funcs_gen.try_add_user_func(jar_id, functions_body=[func_body]).status \
                       == 400
