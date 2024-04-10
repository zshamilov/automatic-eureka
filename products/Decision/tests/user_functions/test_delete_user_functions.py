import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import UserJarFunctionsDto, UserJarFullViewDto, UserFunctionShortView, \
    UserFunctionUploadView, UserFunctionShortInfo, ResponseDto
from products.Decision.framework.steps.decision_steps_user_functions import get_jar_files_list, upload_jar_file, \
    delete_jar_file, get_functions_list, create_user_function, delete_user_functions


@allure.epic("Настройка функций")
@allure.feature("Удаление пользовательской функции")
@pytest.mark.scenario("DEV-6110")
class TestUserFuncsDelete:

    @allure.story("Jar файл возможно удалить")
    @allure.title("Удалить загруженный jar-file, проверить, что не найден")
    @allure.link("DEV-6110")
    @pytest.mark.smoke
    def test_delete_jar_file(self, super_user):
        with allure.step("Загрузка jar файл в систему"):
            upload_resp: UserJarFunctionsDto = UserJarFunctionsDto(
                **upload_jar_file(
                    super_user, file="products/Decision/resources/user_funcs_testing.jar").body)
            jar_id = upload_resp.jarId
        with allure.step("Удаление загруженного jar файла"):
            delete_jar_file(super_user, jar_id)
        with allure.step("Получение списка jar файлов"):
            files = []
            for file in get_jar_files_list(super_user).body:
                files.append(UserJarFullViewDto.construct(**file))
        with allure.step("Проверка, что загруженный файл не найден"):
            assert not any(file.id == jar_id for file in files)

    @allure.story("Возможно удалить пользовательскую функцию")
    @allure.title("Удалить загруженную функцию, проверить, что не найдена")
    @allure.link("DEV-6110")
    @pytest.mark.smoke
    def test_delete_user_func(self, super_user, upload_funcs_gen):
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
            create_response: ResponseDto = ResponseDto.construct(
                **create_user_function(super_user, jar_id, body=[func_body]).body)
        with allure.step("Получение списка функций"):
            created_function = None
            function_list = []
            for f in get_functions_list(super_user).body["content"]:
                function_list.append(UserFunctionShortInfo.construct(**f))
            for f in function_list:
                if f.description == func_description:
                    created_function = f
        with allure.step("Удаление добавленной функции"):
            delete_user_functions(super_user, func_ids=[str(created_function.id)])
        with allure.step("Получение списка функций"):
            function_list_up = []
            for f in get_functions_list(super_user).body["content"]:
                function_list_up.append(UserFunctionShortInfo.construct(**f))
            for f in function_list_up:
                if f.id == created_function.id:
                    function_found = True
        with allure.step("Проверка, что удалённая функция не найдена"):
            assert not function_found

    @allure.story("Возможно удалить несколько пользовательских функций разом")
    @allure.title("Удалить загруженные пользовательские функции, проверить, что не найдены")
    @allure.link("DEV-6110")
    @pytest.mark.smoke
    def test_batch_delete_user_func(self, super_user, upload_funcs_gen):
        functions_found = False
        with allure.step("Загрузка jar файл в систему"):
            upload_response: UserJarFunctionsDto = upload_funcs_gen.upload_jar_file(
                file="products/Decision/resources/user_funcs_testing.jar")
            jar_id = upload_response.jarId
            functions = upload_response.functions
            add_int_to_str: UserFunctionShortView = UserFunctionShortView.construct()
            for f in functions:
                if f.objectName == "returnString(java.lang.Integer)":
                    add_int_to_str = f
            return_date: UserFunctionShortView = UserFunctionShortView.construct()
            for f in functions:
                if f.objectName == "returnDate()":
                    return_date = f
        with allure.step("Загрузка нескольких пользовательских функций из файла"):
            func_description1 = "made_in_test_" + generate_string()
            func_body1 = UserFunctionUploadView(objectName=add_int_to_str.objectName,
                                                jarFunctionName=add_int_to_str.jarFunctionName,
                                                functionClass=add_int_to_str.functionClass,
                                                resultType="2",
                                                description=func_description1)
            func_description2 = "made_in_test_" + generate_string()
            func_body2 = UserFunctionUploadView(objectName=return_date.objectName,
                                                jarFunctionName=return_date.jarFunctionName,
                                                functionClass=return_date.functionClass,
                                                resultType="3",
                                                description=func_description2)
            create_response: ResponseDto = ResponseDto.construct(
                **create_user_function(super_user, jar_id, body=[func_body1, func_body2]).body)
        with allure.step("Получение списка функций"):
            created_function1 = None
            created_function2 = None
            function_list = []
            for f in get_functions_list(super_user).body["content"]:
                function_list.append(UserFunctionShortInfo.construct(**f))
            for f in function_list:
                if f.description == func_description1:
                    created_function1 = f
                if f.description == func_description2:
                    created_function2 = f
        with allure.step("Удаление добавленных функции"):
            delete_user_functions(super_user, func_ids=[str(created_function1.id),
                                                        str(created_function2.id)])
        with allure.step("Получение списка функций"):
            function_list_up = []
            for f in get_functions_list(super_user).body["content"]:
                function_list_up.append(UserFunctionShortInfo.construct(**f))
            for f in function_list_up:
                if f.id == created_function1.id or f.id == created_function2.id:
                    functions_found = True
        with allure.step("Проверка, что удалённые функции не найдены"):
            assert not functions_found
