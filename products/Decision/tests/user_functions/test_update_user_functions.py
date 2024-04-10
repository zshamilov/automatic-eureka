import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import UserFunctionShortInfo, UserFunctionUpdateDto
from products.Decision.framework.steps.decision_steps_user_functions import update_user_function, get_functions_list


@allure.epic("Настройка функций")
@allure.feature("Удаление пользовательской функции")
@pytest.mark.scenario("DEV-6110")
class TestUserFuncsUpdate:

    @allure.story("Описание пользовательской функции не должно превосходить 100 символов")
    @allure.title("Проверить длину описания пользовательской функции")
    @pytest.mark.parametrize("length, status", [(99, 200), (100, 200)])
    def test_update_uf_descr_length(self, super_user, upload_funcs_gen, length, status):
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2"
            )
            up_descr = "made_in_test_updated" + generate_string(length)
            func_id = user_func.id
        with allure.step("Обновление описания функции"):
            update_body = UserFunctionUpdateDto(objectName="returnString(java.lang.Integer)",
                                                resultType="2",
                                                description=up_descr)
            up_resp = update_user_function(super_user, function_id=func_id, body=update_body)
        with allure.step("Проверка доступности обновления в зависимости от длины описания"):
            assert up_resp.status == status

    @allure.story("Пользовательской функции возмоно обновить описание")
    @allure.title("Обновить описание пользовательской функции")
    @allure.link("DEV-6110")
    @pytest.mark.smoke
    def test_update_uf_descr(self, super_user, upload_funcs_gen):
        function_updated = False
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2"
            )
            up_descr = "made_in_test_updated" + generate_string()
            func_id = user_func.id
        with allure.step("Обновление описания функции"):
            update_body = UserFunctionUpdateDto(objectName="returnString(java.lang.Integer)",
                                                resultType="2",
                                                description=up_descr)
            update_user_function(super_user, function_id=func_id, body=update_body)
        with allure.step("Получение списка функций"):
            function_list = []
            for f in get_functions_list(super_user).body["content"]:
                function_list.append(UserFunctionShortInfo.construct(**f))
            for f in function_list:
                if f.id == user_func.id:
                    if f.description == up_descr:
                        function_updated = True
                    break
        with allure.step("Проверка, что описание обновлено"):
            assert function_updated

    @allure.story("Возможно обновить тип результирующего значения на доступный примитив")
    @allure.title("Проверить примитивы на возможность обновления результирующего значения")
    @pytest.mark.parametrize("r_type, status", [("0", 200),
                                                ("7", 200)])
    def test_update_uf_result_type(self, super_user, upload_funcs_gen, r_type, status):
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2"
            )
            up_descr = "made_in_test_updated" + generate_string()
            func_id = user_func.id
        with allure.step("Обновление описания функции"):
            update_body = UserFunctionUpdateDto(objectName="returnString(java.lang.Integer)",
                                                resultType=r_type,
                                                description=up_descr)
            up_resp = update_user_function(super_user, function_id=func_id, body=update_body)
        with allure.step("Проверка доступности обновления в зависимости от длины описания"):
            assert up_resp.status == status

    @allure.story("Возможно обновить тип результирующего значения на доступный примитив")
    @allure.title("Проверить примитивы на возможность обновления результирующего значения")
    @pytest.mark.parametrize("r_type, status", [("-1", 400),
                                                ("10", 400)])
    def test_update_uf_result_type_neg(self, super_user, upload_funcs_gen, r_type, status):
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2"
            )
            up_descr = "made_in_test_updated" + generate_string()
            func_id = user_func.id
        with allure.step("Обновление описания функции"):
            update_body = UserFunctionUpdateDto(objectName="returnString(java.lang.Integer)",
                                                resultType=r_type,
                                                description=up_descr)
        with allure.step("Проверка доступности обновления в зависимости от длины описания"):
            with pytest.raises(HTTPError):
                assert update_user_function(super_user, function_id=func_id, body=update_body).status \
                       == status

    @allure.story("Невозможно обновить имя и аргументы функции не соответствующие указанным в файле")
    @allure.title("Обновить имя на некорректное, проверить, что обновления не произошло")
    @pytest.mark.parametrize("name_bad", ["returnString(incorrect1, incorrect2)",
                                          "oh_that's_very_wrong_name(java.lang.Integer)"])
    def test_update_uf_args_neg(self, super_user, upload_funcs_gen, name_bad):
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2"
            )
            up_name = name_bad
            func_id = user_func.id
        with allure.step("Обновление имени функции, указав некорректные аргументы"):
            update_body = UserFunctionUpdateDto(objectName=up_name,
                                                resultType="2",
                                                description="made_in_test_updated" + generate_string())
        with allure.step("Проверка, что не произошло некорректного обновления аргументов"):
            with pytest.raises(HTTPError):
                assert update_user_function(super_user, function_id=func_id, body=update_body).status\
                       == 400
