import base64
import datetime

import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import CommunicationChannelShortInfoDto, ScriptFullView, \
    ScriptVariableViewWithoutVersionIdDto, DataSourceType1, ResponseDto, CommunicationChannelFullViewDto, \
    CommunicationChannelWithVariablesDto, CommunicationPage, CommunicationChannelCatalogShortInfoDto
from products.Decision.framework.steps.decision_steps_communication_api import get_channel_list, \
    get_communication_channel, get_channel_variables, get_channel_list_catalog_content
from products.Decision.utilities.communication_constructors import *


@allure.epic("Каналы коммуникации")
@allure.feature("Обновление канала")
class TestCommunicationInfo:

    @allure.story("Каждый элемент списка каналов коммуникаций содержит поля: communicationChannelId, "
                  "communicationChannelName, versionId, createDt, changeDt")
    @allure.title("Запросить список каналов, проверить поля")
    @pytest.mark.scenario("DEV-10141")
    @pytest.mark.smoke
    def test_communication_list(self, super_user):
        with allure.step("Получение списка каналов коммуникаций"):
            channel_list = []
            comms_page: CommunicationPage = CommunicationPage.construct(**get_channel_list(super_user).body)
            for channel in comms_page.content:
                channel_list.append(CommunicationChannelShortInfoDto.construct(**channel))
        with allure.step("Проверка, что в списке содержится необходимая информация"):
            channel_contain_req_fields = next((channel for channel in channel_list if
                                               channel.versionId is not None
                                               and channel.changeDt is not None
                                               and channel.communicationChannelId is not None
                                               and channel.objectName is not None), True)

            assert len(channel_list) != 0 and channel_contain_req_fields

    @allure.story("Канала коммуникаций можно найти по идентификатору версии")
    @allure.title("Создать канал, запросить информацию, проверить, что найден")
    @pytest.mark.scenario("DEV-10141")
    @pytest.mark.smoke
    def test_communication_information(self, super_user,
                                       create_python_code_int_vars,
                                       create_communication_gen):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций"):
            channel_name = "channel_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=inp_var.variableName,
                                              primitive_type_id=inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Создание канала коммуникаций"):
            create_response: ResponseDto = create_communication_gen.create_communication_channel(
                communication_channel_body=comm)
        with allure.step("Поиск канала коммуникаций по идентификатору версии"):
            search_response = CommunicationChannelFullViewDto.construct(
                **get_communication_channel(super_user, version_id=create_response.uuid).body)
        with allure.step("Проверка, что канал коммуникаций найден и его имя соответствует заданному"):
            assert search_response.objectName == channel_name \
                   and search_response.communicationChannelId is not None \
                   and search_response.versionId == create_response.uuid \
                   and search_response.communicationVariables[0]["scriptVariableName"] == inp_var.variableName

    @allure.story("Возможно получить информацию о переменных канала коммуникаций")
    @allure.title("Создать канал, запросить информацию о переменных")
    @pytest.mark.scenario("DEV-10141")
    @pytest.mark.smoke
    def test_communication_variables(self, super_user,
                                     create_python_code_int_vars,
                                     create_communication_gen):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций"):
            channel_name = "channel_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=inp_var.variableName,
                                              primitive_type_id=inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Создание канала коммуникаций"):
            create_response: ResponseDto = create_communication_gen.create_communication_channel(
                communication_channel_body=comm)
        with allure.step("Получение информации о переменных канала"):
            comm_with_vars: CommunicationChannelWithVariablesDto = CommunicationChannelWithVariablesDto(
                **get_channel_variables(super_user, version_id=create_response.uuid).body)
        with allure.step("Проверка, что информацию о канале с переменными вернулась корректной и что переменной "
                         "присвоен идентификатор"):
            assert comm_with_vars.communicationChannelId is not None \
                   and str(comm_with_vars.versionId) == create_response.uuid \
                   and comm_with_vars.communicationVariables[0].id is not None \
                   and len(comm_with_vars.communicationVariables) != 0

    @allure.story("Корректно отрабатывает ограничение размера выдачи")
    @allure.title("Получить список каналов коммуникаций с ограничением по размеру выдачи")
    @pytest.mark.scenario("DEV-6400")
    def test_communication_page_size(self, super_user):
        list_query_str = '{"filters":[],"sorts":[],"searchBy":"","page":1,"size":2}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка каналов с ограничением в 2 элемента"):
            comms_page: CommunicationPage = CommunicationPage.construct(**
                                                                        get_channel_list(super_user, query={
                                                                            "searchRequest": list_query.decode(
                                                                                "utf-8")}).body)
        with allure.step("Проверка, что было получено ровно 2 элемента"):
            assert len(comms_page.content) == 2

    @allure.story("Сортировка по возрастанию корректно отрабатывает для columnName:"
                  " communicationChannelName, communicationChannelId, changeDt, createByUser")
    @allure.title("Получить список каналов коммуникаций с сортировкой по возрастанию")
    @pytest.mark.scenario("DEV-6400")
    def test_communication_sort_date_forward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"ASC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        channel_list = []
        with allure.step("Получение списка каналов с сортировкой по возрастанию"):
            comms_page: CommunicationPage = CommunicationPage.construct(**
                                                                        get_channel_list(super_user, query={
                                                                            "searchRequest": list_query.decode(
                                                                                "utf-8")}).body)
            for channel in comms_page.content:
                channel_list.append(CommunicationChannelShortInfoDto.construct(**channel))
        with allure.step("Проверка, что элементы в списке отсортированы по возрастанию по дате"):
            sort_correct_counter = 0
            for i in range(len(channel_list) - 1):
                current_date = datetime.datetime.strptime(channel_list[i].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                next_date = datetime.datetime.strptime(channel_list[i + 1].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                if current_date < next_date:
                    sort_correct_counter += 1
            assert sort_correct_counter == len(channel_list) - 1

    @allure.story("Сортировка по возрастанию корректно отрабатывает для columnName:"
                  " communicationChannelName, communicationChannelId, changeDt, createByUser")
    @allure.title("Получить список каналов коммуникаций с сортировкой имён по возрастанию")
    @pytest.mark.scenario("DEV-6400")
    @pytest.mark.skip("need fix")
    def test_communication_sort_name_forward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"objectName","direction":"ASC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        channel_list = []
        with allure.step("Получение списка каналов с сортировкой по возрастанию"):
            comms_page: CommunicationPage = CommunicationPage.construct(**
                                                                        get_channel_list(super_user, query={
                                                                            "searchRequest": list_query.decode(
                                                                                "utf-8")}).body)
            for channel in comms_page.content:
                channel_list.append(CommunicationChannelShortInfoDto.construct(**channel))
        with allure.step("Проверка, что элементы в списке отсортированы по возрастанию по имени"):
            sort_correct_counter = 0
            for i in range(len(channel_list) - 1):
                current_name = channel_list[i].objectName.lower()
                next_name = channel_list[i + 1].objectName.lower()
                if current_name < next_name:
                    sort_correct_counter += 1
                else:
                    print(current_name)
                    print(next_name)
            assert sort_correct_counter == len(channel_list) - 1

    @allure.story("Сортировка по убыванию корректно отрабатывает для columnName:"
                  " communicationChannelName, communicationChannelId, changeDt, createByUser")
    @allure.title("Получить список каналов коммуникаций с сортировкой по убыванию")
    @pytest.mark.scenario("DEV-6400")
    def test_communication_sort_date_backward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"DESC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        channel_list = []
        with allure.step("Получение списка каналов с сортировкой по убыванию"):
            comms_page: CommunicationPage = CommunicationPage.construct(**
                                                                        get_channel_list(super_user, query={
                                                                            "searchRequest": list_query.decode(
                                                                                "utf-8")}).body)
            for channel in comms_page.content:
                channel_list.append(CommunicationChannelShortInfoDto.construct(**channel))
        with allure.step("Проверка, что элементы в списке отсортированы по убыванию по дате"):
            sort_correct_counter = 0
            for i in range(len(channel_list) - 1):
                current_date = datetime.datetime.strptime(channel_list[i].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                next_date = datetime.datetime.strptime(channel_list[i + 1].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                if current_date > next_date:
                    sort_correct_counter += 1
            assert sort_correct_counter == len(channel_list) - 1

    @allure.story(
        "Сортировка по убыванию корректно отрабатывает для columnName:"
        " communicationChannelName, communicationChannelId, changeDt, createByUser")
    @allure.title("Получить список каналов коммуникаций с сортировкой имён по убыванию")
    @pytest.mark.scenario("DEV-6400")
    @pytest.mark.skip("need fix")
    def test_communication_sort_name_backward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"objectName","direction":"DESC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        channel_list = []
        with allure.step("Получение списка каналов с сортировкой по возрастанию"):
            comms_page: CommunicationPage = CommunicationPage.construct(**
                                                                        get_channel_list(super_user, query={
                                                                            "searchRequest": list_query.decode(
                                                                                "utf-8")}).body)
            for channel in comms_page.content:
                channel_list.append(CommunicationChannelShortInfoDto.construct(**channel))
        with allure.step("Проверка, что элементы в списке отсортированы по убыванию по имени"):
            sort_correct_counter = 0
            for i in range(len(channel_list) - 1):
                current_name = channel_list[i].objectName.lower()
                next_name = channel_list[i + 1].objectName.lower()
                if current_name > next_name:
                    sort_correct_counter += 1
                else:
                    print(current_name)
                    print(next_name)
            assert sort_correct_counter == len(channel_list) - 1

    @allure.story("При отсутствии query - кол-во элементов 20, если totalElements не меньше 20")
    @allure.title("Проверка, что возможно получить список каналов коммуникаций без указания параметров выдачи")
    @pytest.mark.scenario("DEV-6400")
    def test_communication_page_defaults(self, super_user):
        with allure.step("Получение списка каналов без указания параметров выдачи"):
            communication_page_response = get_channel_list(super_user, query={})
        with allure.step("Проверка, что успешно"):
            assert communication_page_response.status == 200 and \
                   len(communication_page_response.body["content"]) <= 20

    @allure.story("поле searchBy корректно осуществляет поиск по полям communicationChannelName, по принципу: "
                  "communicationChannelName LIKE %<searchByValue>% OR communicationChannelId LIKE %<searchByValue>% ")
    @allure.title("Получить список каналов коммуникаций с ограничением выдачи по имени элемента")
    @pytest.mark.scenario("DEV-6400")
    def test_communication_page_search_by(self, super_user, create_python_code_int_vars, create_communication_gen):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций"):
            channel_name = "channel_for_name_filter_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=inp_var.variableName,
                                              primitive_type_id=inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Создание канала коммуникаций"):
            create_communication_gen.create_communication_channel(
                communication_channel_body=comm)
        with allure.step("Задание критериев отбора выдачи"):
            reference_channel_name = channel_name
        with allure.step("Получение списка каналов с ограничением выдачи по имени элемента"):
            comms_page_up: list[CommunicationChannelCatalogShortInfoDto] = get_channel_list_catalog_content(
                super_user, filtered_name=reference_channel_name)
        with allure.step("Получение списка каналов с ограничением выдачи по имени элемента"):
            assert len(comms_page_up) == 1 and \
                   all(channel.objectName == reference_channel_name for channel in
                       comms_page_up)

    @allure.story("Фильтры должны корректно отрабатывать для columnName: createByUser и ChangeDt")
    @allure.title("При запросе списка коммуникаций выставить фильтр даты, проверить, что элементы выдачи корректны")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_communication_filter_date(self, super_user):
        # list_query_str = '{"filters":[{"columnName":"changeDt","operator":"BETWEEN","value":"05-12-2022 15:03:16","valueTo":"12-12-2022 10:22:01"}],"sorts":[],"searchBy":"","page":1,"size":20}'
        filter_wrong = False
        start_date_pure = datetime.date.today() - datetime.timedelta(days=15)
        finish_date_pure = datetime.date.today()
        start_date = start_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        finish_date = finish_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        list_query_str = f'{{"filters":[{{"columnName":"changeDt","operator":"BETWEEN","value":"{start_date}","valueTo":"{finish_date}"}}],' \
                         f'"sorts":[],"searchBy":"","page":1,"size":20}}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        channel_list = []
        with allure.step("Получение списка каналов с фильтром по дате изменения"):
            comms_page: CommunicationPage = CommunicationPage.construct(**
                                                                        get_channel_list(super_user, query={
                                                                            "searchRequest": list_query.decode(
                                                                                "utf-8")}).body)
            for channel in comms_page.content:
                channel_list.append(CommunicationChannelShortInfoDto.construct(**channel))
        with allure.step("Проверка, что все элементы выдачи попали в границы фильтрации"):
            for channel in channel_list:
                current_date = datetime.datetime.strptime(f'{channel.changeDt}', "%Y-%m-%d %H:%M:%S.%f").date()
                if not (start_date_pure <= current_date <= finish_date_pure):
                    filter_wrong = True
        assert not filter_wrong

    @allure.story("В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber")
    @allure.title("Получить список всех каналов, проверить, что totalElements соответствует длине списка")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_communication_total_elements_correct(self, super_user):
        with allure.step("Получение списка каналов"):
            comms_page: CommunicationPage = CommunicationPage.construct(
                **get_channel_list(super_user).body)
            assert comms_page.totalElements == len(comms_page.content)

    @allure.story("В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber")
    @allure.title("Получить список всех каналов, проверить, что totalPages соответствует длине списка,"
                  " делённой на 20 плюс 1")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    @pytest.mark.skip("need fix")
    def test_communication_total_pages_correct(self, super_user):
        with allure.step("Получение списка каналов"):
            comms_page: CommunicationPage = CommunicationPage.construct(
                **get_channel_list(super_user).body)
            assert comms_page.totalPages == len(comms_page.content)//20 + 1

    @allure.story("В ответе для base64 с параметром page в ответ приходит current page = page-1")
    @allure.title("Получить список каналов с заданной страницей, проверить, что текущая страница"
                  " такая же, как указано в параметре минус 1")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_communication_current_page_correct(self, super_user):
        page_num = 1
        list_query_str = f'{{"filters":[],"sorts":[],"searchBy":"","page":{page_num},"size":10}}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка каналов с фильтром по выдаче"):
            comms_page: CommunicationPage = CommunicationPage.construct(
                **get_channel_list(super_user, query={"searchRequest": list_query.decode(
                                                                                "utf-8")}).body)
            assert comms_page.currentPageNumber == page_num - 1
