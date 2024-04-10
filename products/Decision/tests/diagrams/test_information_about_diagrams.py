import base64
import datetime
import pytest
import glamor as allure

from products.Decision.framework.model import DiagramShortInfoView, DiagramViewDto, DiagramPage
from products.Decision.framework.steps.decision_steps_diagram import diagrams_list, get_diagram_by_version, \
    diagram_list_by_name
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description


@allure.epic("Диаграммы")
@allure.feature("Информация о диаграммах")
class TestDiagramsInfo:

    @allure.story("В списке диаграмм отображаются необходимые поля о всех диаграммах")
    @allure.title("Получаем список диаграмм, смотрим, что корректный")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.smoke
    def test_get_diagrams_list(self, super_user):
        with allure.step("Получение списка диаграмм"):
            result = diagrams_list(super_user)
            diagram_list: [DiagramShortInfoView] = result.body["content"]
        with allure.step("Проверка, что в списке содержатся необходимые поля"):
            diagrams_contain_req_fields = next((diagram for diagram in diagram_list if diagram["diagramId"] is not None
                                                and diagram["versionId"] is not None
                                                and diagram["lastChangeByUser"] is not None
                                                and diagram["changeDt"] is not None
                                                and diagram["objectName"] is not None), False)

            assert result.status == 200 and len(diagram_list) != 0 and diagrams_contain_req_fields

    @allure.story("Информация о всех версиях диаграммы должна отображаться для каждой диаграммы")
    @allure.title("Создать диаграмму, сохранить как новую, проверить, что появилась в списке")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-727")
    def test_diagram_as_new_appear_in_list(self, super_user, create_temp_diagram, save_diagrams_gen):
        diagram_found_under_new_name = False
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            version_id = diagram_template["versionId"]
        with allure.step("генерация информации о новой диаграмме"):
            new_diagram_name = "diagram_as_new" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            diagram_description = 'new diagram created in test'
        with allure.step("Сохранение временной диаграммы, как новой"):
            create_as_new_result = save_diagrams_gen.save_diagram_as_new(diagram_id, version_id, new_diagram_name,
                                                                         diagram_description).body
            version_uuid = create_as_new_result["uuid"]
        with allure.step("Получение списка диаграмм"):
            response_diagram_list = diagram_list_by_name(super_user, new_diagram_name)
            diagram_list: [DiagramShortInfoView] = response_diagram_list
        with allure.step("Проверка, что диаграмма, сохранённая, как новая найдена в списке"):
            for diagram in diagram_list:
                if diagram["objectName"] == new_diagram_name and diagram["versionId"] == version_uuid:
                    diagram_found_under_new_name = True
            assert diagram_found_under_new_name 

    @allure.story("Диаграмму можно найти по айди версии")
    @allure.title("Создать диаграмму, сохранить, найти информацию по айди")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.smoke
    def test_find_diagram_by_id(self, super_user, create_and_save_empty_diagram_without_info):
        with allure.step("Создание и сохранение диаграммы"):
            save_response_dto = create_and_save_empty_diagram_without_info
            version_id = save_response_dto["uuid"]
        with allure.step("Поиск диаграммы по айди версии"):
            get_diagram_by_version_response = get_diagram_by_version(super_user, version_id)
            diagram_info = DiagramViewDto.construct(**get_diagram_by_version_response.body)
        with allure.step("Проверка, что диаграмма нашлась"):
            assert get_diagram_by_version_response

    @allure.story("Диаграмма с временной версией не должна отображаться в списке диаграмм")
    @allure.title("Создать диаграмму без сохранения, проверить, что не появилась в списке")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_get_unsaved_diagram(self, super_user, create_temp_diagram):
        diagram_found = False
        with allure.step("Создание временной версии диаграммы"):
            diagram_template = create_temp_diagram
            temp_version_name = diagram_template["objectName"]
        with allure.step("Получение списка диаграмм"):
            result = diagrams_list(super_user)
            diagram_list: [DiagramShortInfoView] = result.body["content"]
        with allure.step("Проверка на то, что диаграмма под временным именем не найдена в списке"):
            for diagram in diagram_list:
                if diagram["objectName"] == temp_version_name:
                    diagram_found = True
            assert not diagram_found

    @allure.story("Фильтры должны корректно отрабатывать для columnName: createByUser и ChangeDt")
    @allure.title("При запросе списка диаграмм выставить фильтр даты, проверить, что элементы выдачи корректны")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_diagram_list_filter_date(self, super_user):
        filter_wrong = False
        start_date_pure = datetime.date.today() - datetime.timedelta(days=15)
        finish_date_pure = datetime.date.today()
        start_date = start_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        finish_date = finish_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        filtered_diagrams = []
        list_query_str = f'{{"filters":[{{"columnName":"changeDt","operator":"BETWEEN","value":"{start_date}","valueTo":"{finish_date}"}}],' \
                         f'"sorts":[],"searchBy":"","page":1,"size":20}}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        with allure.step("Получение списка диаграмм"):
            diagram_page: DiagramPage = DiagramPage.construct(**diagrams_list(super_user, query={
                "searchRequest": list_query.decode(
                    "utf-8")}).body)
        for diagram in diagram_page.content:
            filtered_diagrams.append(DiagramShortInfoView.construct(**diagram))
        with allure.step("Проверка, что все элементы выдачи попали в границы фильтрации"):
            for diagram in filtered_diagrams:
                current_date = datetime.datetime.strptime(f'{diagram.changeDt}', "%Y-%m-%d %H:%M:%S.%f").date()
                if not (start_date_pure <= current_date <= finish_date_pure):
                    filter_wrong = True
        assert not filter_wrong

    @allure.story("Сортировка по возрастанию корректно отрабатывает для columnName:"
                  " diagramName, diagramId, changeDt, createByUser")
    @allure.title("Получить список диаграмм с сортировкой по возрастанию")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_diagram_sort_date_forward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"ASC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        filtered_diagrams = []
        with allure.step("Получение списка диаграмм"):
            diagram_page: DiagramPage = DiagramPage.construct(**diagrams_list(super_user, query={
                "searchRequest": list_query.decode(
                    "utf-8")}).body)
        for diagram in diagram_page.content:
            filtered_diagrams.append(DiagramShortInfoView.construct(**diagram))
        with allure.step("Проверка, что элементы в списке отсортированы по возрастанию по дате"):
            sort_correct_counter = 0
            for i in range(len(filtered_diagrams) - 1):
                current_date = datetime.datetime.strptime(filtered_diagrams[i].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                next_date = datetime.datetime.strptime(filtered_diagrams[i+1].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                if current_date < next_date:
                    sort_correct_counter += 1
                else:
                    print(current_date == next_date)
                    print(current_date > next_date)
                    print("CURRENT ERROR DIAGRAM")
                    print(filtered_diagrams[i].objectName)
                    print(filtered_diagrams[i].changeDt)
                    print("NEXT ERROR DIAGRAM")
                    print(filtered_diagrams[i+1].objectName)
                    print(filtered_diagrams[i+1].changeDt)
            assert sort_correct_counter == len(filtered_diagrams) - 1

    @allure.story("Сортировка по убыванию корректно отрабатывает для columnName:"
                  " diagramName, diagramId, changeDt, createByUser")
    @allure.title("Получить список диаграмм с сортировкой по убыванию")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_diagram_sort_date_backward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"DESC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        filtered_diagrams = []
        with allure.step("Получение списка диаграмм"):
            diagram_page: DiagramPage = DiagramPage.construct(**diagrams_list(super_user, query={
                "searchRequest": list_query.decode(
                    "utf-8")}).body)
        for diagram in diagram_page.content:
            filtered_diagrams.append(DiagramShortInfoView.construct(**diagram))
        with allure.step("Проверка, что элементы в списке отсортированы по возрастанию по дате"):
            sort_correct_counter = 0
            for i in range(len(filtered_diagrams) - 1):
                current_date = datetime.datetime.strptime(filtered_diagrams[i].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                next_date = datetime.datetime.strptime(filtered_diagrams[i + 1].changeDt, "%Y-%m-%d %H:%M:%S.%f")
                if current_date > next_date:
                    sort_correct_counter += 1
                else:
                    print(current_date == next_date)
                    print(current_date > next_date)
                    print("CURRENT ERROR DIAGRAM")
                    print(filtered_diagrams[i].objectName)
                    print(filtered_diagrams[i].changeDt)
                    print("NEXT ERROR DIAGRAM")
                    print(filtered_diagrams[i + 1].objectName)
                    print(filtered_diagrams[i + 1].changeDt)
            assert sort_correct_counter == len(filtered_diagrams) - 1

    @allure.story("В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber")
    @allure.title("Получить список всех диаграмм, проверить, что totalElements соответствует длине списка")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_diagrams_total_elements_correct(self, super_user):
        with allure.step("Получение списка диаграмм"):
            diagram_page: DiagramPage = DiagramPage.construct(
                **diagrams_list(super_user).body)
            assert len(diagram_page.content)*(diagram_page.totalPages - 1) <= diagram_page.totalElements \
                   <= len(diagram_page.content)*diagram_page.totalPages

    @allure.story("В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber")
    @allure.title(
        "Получить список всех диаграмм, проверить, что totalPages соответствует длине списка, делённой на 20 плюс 1")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_diagrams_total_pages_correct(self, super_user):
        list_query_str = '{"filters":[],"sorts":[],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        with allure.step("Получение ограниченного списка диаграмм для проверки"):
            diagram_page1: DiagramPage = DiagramPage.construct(
                **diagrams_list(super_user, query={"searchRequest": list_query.decode(
                    "utf-8")}).body)
            assert diagram_page1.totalPages == diagram_page1.totalElements // 20 + 1

    @allure.story("В ответе для base64 с параметром page в ответ приходит current page = page-1")
    @allure.title(
        "Получить список диаграмм с заданной страницей, проверить, что текущая страница такая же, как указано в параметре минус 1")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_diagrams_current_page_correct(self, super_user):
        page_num = 2
        list_query_str = f'{{"filters":[],"sorts":[],"searchBy":"","page":{page_num},"size":10}}'
        list_query = base64.b64encode(bytes(list_query_str, 'utf-8'))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка диаграмм с фильтром по выдаче"):
            diagram_page: DiagramPage = DiagramPage.construct(
                **diagrams_list(super_user, query={"searchRequest": list_query.decode(
                    "utf-8")}).body)
            assert diagram_page.currentPageNumber == page_num - 1

    @allure.story("При отсутствии query - кол-во элементов 20, если totalElements не меньше 20")
    @allure.title("Проверка, что возможно получить список диаграмм без указания параметров выдачи")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_diagrams_page_defaults(self, super_user):
        with allure.step("Получение списка диаграмм без указания параметров выдачи"):
            diagram_page_response = diagrams_list(super_user, query={})
        with allure.step("Проверка, что успешно"):
            assert diagram_page_response.status == 200 and \
                   len(diagram_page_response.body["content"]) <= 20
