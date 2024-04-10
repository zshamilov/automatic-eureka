import datetime

import allure
import pytest

from products.Decision.framework.model import UserFunctionShortInfo, FunctionGetFullView
from products.Decision.framework.steps.decision_steps_references import get_function_list
from products.Decision.framework.steps.decision_steps_user_functions import get_functions_list_filter_date, \
    get_functions_list_sort


@allure.epic("Настройка функций")
@allure.feature("Удаление пользовательской функции")
class TestUserFuncsUpdate:

    @allure.story("Информация о пользовательских функциях отображается в списке всех функций")
    @allure.title("Добавить пользовательскую функцию, проверить список всех функций")
    @pytest.mark.scenario("DEV-6110")
    @allure.link("DEV-6110")
    @pytest.mark.smoke
    def test_uf_appears_in_all_func_list(self, super_user, upload_funcs_gen):
        user_func_found_in_all_func_list = False
        with allure.step("Добавление пользовательской функции"):
            user_func: UserFunctionShortInfo = upload_funcs_gen.add_user_func_from_file(
                file="products/Decision/resources/user_funcs_testing.jar",
                func_name="returnString(java.lang.Integer)",
                func_result_type="2"
            )
            func_id = user_func.id
        with allure.step("Получение списка всех функций"):
            all_func_list = []
            for f in get_function_list(super_user).body.values():
                all_func_list.append(FunctionGetFullView.construct(**f))
            for f in all_func_list:
                if f.functionId == func_id and f.isExternal:
                    user_func_found_in_all_func_list = True
        with allure.step("Проверка, что пользовательская функция появилась в списке всех функций"):
            assert user_func_found_in_all_func_list

    @allure.story("Пользователь может выставить фильтр по дате в списке пользовательских функций")
    @allure.title("Выставить фильтр по дате, найти файл функций")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_date_filter_in_user_func_list(self, super_user):
        filter_wrong = False
        start_date = "2023-03-10 00:00:00.000"
        finish_date = "2024-01-18 00:00:00.000"
        check_start_date = datetime.datetime.strptime(
            f"2023-03-10 00:00:00.000", "%Y-%m-%d %H:%M:%S.%f"
        )
        check_finish_date = datetime.datetime.strptime(
            f"2024-01-18 00:00:00.000", "%Y-%m-%d %H:%M:%S.%f"
        )
        with allure.step("Выставление фильтра по дате и получение списка"):
            func_list = get_functions_list_filter_date(super_user, date_from=start_date, date_to=finish_date)
        with allure.step("Проверка, что все элементы выдачи попали в границы фильтрации"):
            for func in func_list:
                current_date = datetime.datetime.strptime(func.changeDt, "%Y-%m-%d %H:%M:%S.%f")
                if not (check_start_date <= current_date <= check_finish_date):
                    filter_wrong = True
        assert not filter_wrong

    @allure.story("Пользователь может выставить сортировку по возрастанию даты"
                  " в списке пользовательских функций")
    @allure.title("Выставить сортировку вверх по дате")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_date_sort_up_in_user_func_list(self, super_user):
        filter_wrong = False
        sort = "ASC"
        column = "changeDt"
        with allure.step("Выставление сортировки по дате вверх и получение списка"):
            func_list = get_functions_list_sort(user=super_user, sort=sort, column=column)
        with allure.step("Проверка, что элементы выдачи отсортированы в порядке возрастания"):
            prev_date = "0000-00-00 00:00:00.000"
            for func in func_list:
                current_date = func.changeDt
                if not (prev_date <= current_date):
                    filter_wrong = True
                prev_date = current_date
        assert not filter_wrong

    @allure.story("Пользователь может выставить сортировку по убыванию даты"
                  " в списке пользовательских функций")
    @allure.title("Выставить сортировку вниз по дате")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_date_sort_down_in_user_func_list(self, super_user):
        filter_wrong = False
        sort = "DESC"
        column = "changeDt"
        with allure.step("Выставление сортировки по дате вниз и получение списка"):
            func_list = get_functions_list_sort(user=super_user, sort=sort, column=column)
        with allure.step("Проверка, что элементы выдачи отсортированы в порядке убывания"):
            prev_date = "9999-99-99 99:99:99.999"
            for func in func_list:
                current_date = func.changeDt
                if not (prev_date >= current_date):
                    filter_wrong = True
                prev_date = current_date
        assert not filter_wrong

    @allure.story("Пользователь может выставить сортировку по возрастанию типа результата"
                  " в списке пользовательских функций")
    @allure.title("Выставить сортировку вверх по типу результата")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    @pytest.mark.skip("need fix")
    def test_type_sort_up_in_user_func_list(self, super_user):
        filter_wrong = False
        sort = "ASC"
        column = "resultType"
        with allure.step("Выставление сортировки по типу результата вверх и получение списка"):
            func_list = get_functions_list_sort(user=super_user, sort=sort, column=column)
        with allure.step("Проверка, что элементы выдачи отсортированы в порядке возрастания"):
            prev_type = ""
            for func in func_list:
                current_type = func.resultType
                if not (prev_type <= current_type):
                    print(current_type)
                    filter_wrong = True
                prev_type = current_type
        assert not filter_wrong

    @allure.story("Пользователь может выставить сортировку по убыванию типа результата"
                  " в списке пользовательских функций")
    @allure.title("Выставить сортировку вниз по типу результата")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    @pytest.mark.skip("need fix")
    def test_type_sort_down_in_user_func_list(self, super_user):
        filter_wrong = False
        sort = "DESC"
        column = "resultType"
        with allure.step("Выставление сортировки по типу результата вниз и получение списка"):
            func_list = get_functions_list_sort(user=super_user, sort=sort, column=column)
        with allure.step("Проверка, что элементы выдачи отсортированы в порядке убывания"):
            prev_type = func_list[0].resultType
            for func in func_list:
                current_type = func.resultType
                if not (prev_type >= current_type):
                    filter_wrong = True
                prev_type = current_type
        assert not filter_wrong

    @allure.story("Пользователь может выставить сортировку по возрастанию имени функции"
                  " в списке пользовательских функций")
    @allure.title("Выставить сортировку вверх по типу результата")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_name_sort_up_in_user_func_list(self, super_user):
        filter_wrong = False
        sort = "ASC"
        column = "objectName"
        with allure.step("Выставление сортировки по имени вверх и получение списка"):
            func_list = get_functions_list_sort(user=super_user, sort=sort, column=column)
        with allure.step("Проверка, что элементы выдачи отсортированы в порядке возрастания"):
            prev_name = ""
            for func in func_list:
                current_name = func.objectName
                if not (prev_name <= current_name):
                    filter_wrong = True
                prev_name = current_name
        assert not filter_wrong

    @allure.story("Пользователь может выставить сортировку по убыванию имени функции"
                  " в списке пользовательских функций")
    @allure.title("Выставить сортировку вниз по типу результата")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_name_sort_down_in_user_func_list(self, super_user):
        filter_wrong = False
        sort = "DESC"
        column = "objectName"
        with allure.step("Выставление сортировки по имени вниз и получение списка"):
            func_list = get_functions_list_sort(user=super_user, sort=sort, column=column)
        with allure.step("Проверка, что элементы выдачи отсортированы в порядке убывания"):
            prev_name = func_list[0].objectName
            for func in func_list:
                current_name = func.objectName
                if not (prev_name >= current_name):
                    filter_wrong = True
                prev_name = current_name
        assert not filter_wrong
