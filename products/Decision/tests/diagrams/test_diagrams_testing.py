import os
import time

import glamor as allure
import pytest
from requests import HTTPError
from typing import List

from products.Decision.framework.model import (
    EmptyTestCreate,
    Locale,
    EmptyTestDto,
    TestInfo,
    TestCreate,
    TestCaseInfo,
    TestCaseGetFullView, TestCaseDebugFullView, DiagramViewDto, DiagramInOutParameterFullViewDto, Status3,
    AttributeGetFullView,
)
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type_attributes
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version, get_filtered_variables
from products.Decision.framework.steps.decision_steps_testing_api import (
    get_tests_list,
    create_empty_test,
    delete_test,
    find_test,
    send_testing_file,
    start_testing,
    update_test,
    get_testing_results,
    get_testcase_info, get_debug_info, get_test_case_result,
)
from products.Decision.utilities.custom_models import VariableParams, IntValueType
from products.Decision.utilities.file_utils import tst_report_validator_values, tst_report_validator_titles, \
    file_testing_get_inout_variables, file_testing_generate_test_cases


@allure.epic("Диаграммы")
@allure.feature("Тестирование диаграмм")
class TestDiagramsTesting:
    @allure.story("Возможно получить список тестов (список пуст)")
    @allure.title("Получить список тестов без тестов")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    def test_diagram_tests_list_without_tests(
            self,
            super_user,
            simple_diagram,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Проверка, что стандартно список пуст"):
            with pytest.raises(HTTPError):
                assert get_tests_list(super_user, query={"diagramId": f"{diagram_id}"}).body["httpCode"] == 404

    @allure.story("Корректно генерируется новый тест")
    @allure.title("Создать тест в диаграмме")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    def test_diagram_create_empty_test(
            self,
            super_user,
            simple_diagram,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step(
                "Проверка, что тест сгенерирован с назначенным айди, именем и таймаутом"
        ):
            assert (
                    create_result.testId is not None
                    and create_result.testName == "Тест_1"
                    and create_result.timeout == 300
            )

    @allure.story("Возможно получить список тестов (в списке есть хотя бы 1 элемент)")
    @allure.title("Создать тест, запросить список тестов")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    def test_diagram_tests_list_with_test(
            self,
            super_user,
            simple_diagram,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Получение списка тестов"):
            test_list = []
            response = get_tests_list(super_user, query={"diagramId": f"{diagram_id}"})
            for test in response.body:
                test_list.append(TestInfo.construct(**test))
        with allure.step("Проверка, что тест появился и данные корректны"):
            assert (
                    len(test_list) == 1
                    and test_list[0].testId == str(create_result.testId)
                    and test_list[0].timeout == create_result.timeout
                    and test_list[0].testName == create_result.testName
            )

    @allure.story("Созданный тест можно удалить")
    @allure.title("Удалить созданный тест")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    def test_diagram_delete_test(
            self,
            super_user,
            simple_diagram,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Удаление теста"):
            delete_test(super_user, create_result.testId)
        with allure.step("Проверка, что удалённый тест пропал из списка"):
            with pytest.raises(HTTPError):
                assert get_tests_list(super_user, query={"diagramId": f"{diagram_id}"}).body["httpCode"] == 404

    @allure.story("Тест можно найти по id")
    @allure.title("Создать тест, найти по айди")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    def test_diagram_find_test_by_id(
            self,
            super_user,
            simple_diagram,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Поиск теста по айди"):
            test_info = TestInfo.construct(
                **find_test(super_user, create_result.testId).body
            )
        with allure.step("Проверка, что удалённый тест пропал из списка"):
            assert (
                    test_info.testId == str(create_result.testId)
                    and test_info.timeout == create_result.timeout
                    and test_info.testName == create_result.testName
            )

    @allure.story("Для теста можно загрузить файл с подготовленными тестовыми данными")
    @allure.title("К созданному тесту добавить файл с тестовыми данными")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_send_testing_file(
            self, super_user, diagram_constructor
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["saved_data"].diagramId
            version_id = diagram_constructor["saved_data"].versionId
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Отправка файла с тестами для пустого теста"):
            send_testing_file(
                super_user,
                create_result.testId,
                file="products/Decision/resources/test_success.xlsx",
            )
        with allure.step("Поиск теста по айди"):
            test_info = TestInfo.construct(
                **find_test(super_user, create_result.testId).body
            )
        assert test_info.testFile == f"/opt/decision/excel/{create_result.testId}.xlsx"

    @allure.issue("DEV-6339")
    @allure.story(
        "Тест с корректными и правильными тестовыми данными должен успешно пройти тестирование"
    )
    @allure.title("Запустить тестирование, дождаться статуса SUCCESS, FAIL")
    @pytest.mark.scenario("DEV-12567")
    @pytest.mark.smoke
    def test_testing_success(
            self,
            super_user,
            diagram_start_finish_test_results
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами и запуск теста"):
            test_result = diagram_start_finish_test_results["test_status"]
        with allure.step("Проверка, что тест сьют прошёл с ожидаемым результатом"):
            assert test_result == Status3.SUCCESS

    @allure.story("Можно скачать файл для тестирования для версии диаграммы")
    @allure.title("Скачать файл для тестирования, проверить, что появился в папке")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_generate_testing_file(
            self,
            super_user,
            diagram_constructor,
            generate_test_file_gen,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["saved_data"].diagramId
            version_id = diagram_constructor["saved_data"].versionId
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Загрузка файла для тестирования диаграммы"):
            file_path = generate_test_file_gen.generate_and_load_testing_file(
                diagram_version_id=version_id
            )
        with allure.step("Проверка, что файл загружен"):
            assert os.path.isfile(file_path)

    @allure.story("Можно скачать файл с тестовыми данными для теста")
    @allure.title("Скачать файл с тестовыми данными, проверить, что появился в папке")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_get_testing_file_for_test(
            self,
            super_user,
            diagram_constructor,
            generate_test_file_gen,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["saved_data"].diagramId
            version_id = diagram_constructor["saved_data"].versionId
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Отправка файла с тестами для пустого теста"):
            send_testing_file(
                super_user,
                create_result.testId,
                file="products/Decision/resources/test_success.xlsx",
            )
        with allure.step("Загрузка файла с тестовыми данными для теста"):
            file_path = generate_test_file_gen.download_testing_file(
                test_id=create_result.testId
            )
        with allure.step("Проверка, что файл загружен"):
            assert os.path.isfile(file_path)

    @allure.story("Тест можно обновить")
    @allure.title("Обновить name и description в тесте")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    def test_diagram_update_test_by_id(
            self,
            super_user,
            simple_diagram,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Обновление имени и описания теста"):
            update_body = TestCreate(
                testName="Тест_обновлённый",
                testFile=None,
                testDescription="Тест обновлён",
                diagramId=version_id,
                timeout=100,
            )
            update_test(super_user, create_result.testId, body=update_body)
        with allure.step("Поиск теста по айди"):
            test_info = TestInfo.construct(
                **find_test(super_user, create_result.testId).body
            )
        with allure.step("Проверка, что удалённый тест пропал из списка"):
            assert (
                    test_info.testDescription == "Тест обновлён"
                    and test_info.testName == "Тест_обновлённый"
            )

    @allure.issue("DEV-6339")
    @allure.story("для пройденного теста можно получить данные о совпадении результата")
    @allure.title("Получить информацию о прохождении теста")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    def test_testing_result(
            self, super_user, diagram_start_finish_test_results
    ):
        # testing_success = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тестирования"):
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            assert all(
                [
                    test_result.caseResult and test_result.caseId is not None
                    for test_result in results
                ]
            )

    @allure.issue("DEV-8499")
    @allure.story("Возможно получить отладочную информацию о прохождении тест-кейса")
    @allure.title("Получить информацию о прохождении теста")
    @pytest.mark.scenario("DEV-5641")
    @pytest.mark.smoke
    def test_testing_result_debug(
            self, super_user, diagram_start_finish_test_results
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тестирования"):
            time.sleep(10)
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_result = get_test_case_result(super_user, test_case_id)
        with allure.step("Получение отладочной информации по узлам"):
            debug_response: TestCaseDebugFullView = TestCaseDebugFullView.construct(
                **get_debug_info(super_user, test_case_id).body)
        with allure.step("Проверка, что отладочная информация приходит"):
            assert debug_response.diagramVersionId is not None and \
                   debug_response.debugNodeInfo is not None

    @allure.issue("DEV-8499")
    @allure.story("отладочная информация содержит данные о всех узлах диаграммы")
    @allure.title("Получить информацию о прохождении сообщения на каждом узле")
    @pytest.mark.scenario("DEV-5641")
    def test_testing_result_debug_node_info(
            self, super_user, diagram_start_finish_test_results
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тестирования"):
            time.sleep(10)
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_result = get_test_case_result(super_user, test_case_id)
        with allure.step("Получение отладочной информации по узлам"):
            debug_response: TestCaseDebugFullView = TestCaseDebugFullView.construct(
                **get_debug_info(super_user, test_case_id).body)
            test_version_id = debug_response.diagramVersionId
            test_diagram_info = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, str(test_version_id)).body)
            real_nodes = set(test_diagram_info.nodes.keys())
        with allure.step("Проверка, что в отладочной информации доступна информация по всем узлам диаграммы"):
            assert set(debug_response.debugNodeInfo.keys()) == real_nodes

    @allure.issue("DEV-8499")
    @allure.story("Отладочная информация содержит данные о значениях всех переменных диаграммы")
    @allure.title("Получить информацию о каждой переменной на каждом узле")
    @pytest.mark.scenario("DEV-5641")
    def test_testing_result_debug_node_info_variables(
            self, super_user, diagram_start_finish_test_results
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
            inp_var: DiagramInOutParameterFullViewDto = diagram_start_finish_test_results["diagram_param_in"]
            out_var: DiagramInOutParameterFullViewDto = diagram_start_finish_test_results["diagram_param_out"]
        with allure.step("Получение результата тестирования"):
            time.sleep(10)
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_result = get_test_case_result(super_user, test_case_id)
        with allure.step("Получение отладочной информации по узлам"):
            debug_response: TestCaseDebugFullView = TestCaseDebugFullView.construct(
                **get_debug_info(super_user, test_case_id).body)
            test_version_id = debug_response.diagramVersionId
        with allure.step("Получение информации о тестовой версии диаграммы"):
            test_diagram_info = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, str(test_version_id)).body)
        with allure.step("Проверка, что ожидаемые переменные находятся на ожидаемых узлах"):
            real_nodes = test_diagram_info.nodes.values()
            test_node_start_id = None
            test_node_finish_id = None
            for node in real_nodes:
                if node["nodeName"] == "Начало":
                    test_node_start_id = node["nodeId"]
                if node["nodeName"] == "Завершение":
                    test_node_finish_id = node["nodeId"]
            debug_nodes_items = debug_response.debugNodeInfo.items()
            for key, value in debug_nodes_items:
                if key == test_node_start_id:
                    if inp_var.parameterName in value["calculatedData"]:
                        start_node_var_correct = True
                if key == test_node_finish_id:
                    if inp_var.parameterName in value["inputData"][0]["inputData"] and \
                            out_var.parameterName in value["calculatedData"]:
                        finish_node_var_correct = True
            assert start_node_var_correct
            assert finish_node_var_correct

    @allure.issue("DEV-6339")
    @allure.story(
        "Для каждого кейса теста можно получить информацию о переменных(testCaseId берётся из GET /test/{"
        "testId}/test_results"
    )
    @pytest.mark.scenario("DEV-14602")
    @allure.title("Получить информацию о тест кейсе")
    @pytest.mark.smoke
    def test_test_case_result(
            self, super_user, diagram_start_finish_test_results
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тест кейса"):
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_info = TestCaseGetFullView.construct(
                **get_testcase_info(super_user, test_case_id).body
            )
        with allure.step("Проверка, что тест кейс успешен и содержит необходимую информацию"):
            assert (
                    case_info.caseId == test_case_id
                    and case_info.caseResult == True
                    and case_info.caseExpResponseJson is not None
                    and case_info.caseRequestJson is not None
            )

    @allure.story("Отчёт по тестированию возможно загрузить")
    @allure.title("Выгрузить отчёт по тестированию")
    @pytest.mark.scenario("DEV-7124")
    @allure.link("DEV-7124")
    @pytest.mark.smoke
    def test_test_report(
            self, super_user, diagram_start_finish_test_results, generate_test_report_gen
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тест кейса"):
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_info = TestCaseGetFullView.construct(
                **get_testcase_info(super_user, test_case_id).body
            )
            file_path = generate_test_report_gen.download_testing_report(test_id)
        with allure.step("Проверка, что файл загружен"):
            assert os.path.isfile(file_path)

    @allure.story("Отчёт по тестированию корректно генерируется")
    @allure.title("Проверить зачения в первом листе отчёта по тестированию")
    @pytest.mark.scenario("DEV-7124")
    @allure.link("DEV-7124")
    @pytest.mark.smoke
    def test_test_report_column_values_page_1(
            self, super_user, diagram_start_finish_test_results, generate_test_report_gen
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тест кейса"):
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_info = TestCaseGetFullView.construct(
                **get_testcase_info(super_user, test_case_id).body
            )
        with allure.step("Выгрузка отчёта по тестировани"):
            file_path = generate_test_report_gen.download_testing_report(test_id)
        with allure.step("Проверка, что на первой странице файла отчёта значения соответствуют ожидаемым"):
            assert tst_report_validator_values(file_path, page=1, test_set_name='Тест_1',
                                               test_set_count=1, test_set_successes=1,
                                               test_set_failures=0, test_set_result='Пройдено успешно')

    @allure.story("Отчёт по тестированию корректно генерируется")
    @allure.title("Проверить текст в первом листе отчёта по тестированию")
    @pytest.mark.scenario("DEV-7124")
    @allure.link("DEV-7124")
    @pytest.mark.smoke
    def test_test_report_content_text_1(
            self, super_user, diagram_start_finish_test_results, generate_test_report_gen
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тест кейса"):
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_info = TestCaseGetFullView.construct(
                **get_testcase_info(super_user, test_case_id).body
            )
        with allure.step("Выгрузка отчёта по тестированию"):
            file_path = generate_test_report_gen.download_testing_report(test_id)
        with allure.step("Проверка, что на второй странице файла отчёта заголовки соответствуют ожидаемым"):
            assert tst_report_validator_titles(file_path, page=1, test_set_name='Название теста',
                                               test_set_count='Количество тестовых наборов',
                                               test_set_successes='Пройдено успешно',
                                               test_set_failures='Не пройдено',
                                               test_set_result='Тестовый набор 1')

    @allure.story("Отчёт по тестированию корректно генерируется")
    @allure.title("Проверить значения во втором листе отчёта по тестированию")
    @pytest.mark.scenario("DEV-7124")
    @allure.link("DEV-7124")
    @pytest.mark.smoke
    def test_test_report_column_values_page_2(
            self, super_user, diagram_start_finish_test_results, generate_test_report_gen
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тест кейса"):
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_info = TestCaseGetFullView.construct(
                **get_testcase_info(super_user, test_case_id).body
            )
        with allure.step("Выгрузка отчёта по тестированию"):
            file_path = generate_test_report_gen.download_testing_report(test_id)
        with allure.step("Проверка, что на второй странице файла отчёта значения соответствуют ожидаемым"):
            assert tst_report_validator_values(file_path, page=2,
                                               out_var_expectation=111, out_var_fact=111,
                                               diagram_exec_status_expectation='"1"',
                                               diagram_exec_status_fact='"1"')

    @allure.story("Отчёт по тестированию корректно генерируется")
    @allure.title("Проверить текст во втором листе отчёта по тестированию")
    @pytest.mark.scenario("DEV-7124")
    @allure.link("DEV-7124")
    @pytest.mark.smoke
    def test_test_report_content_text_2(
            self, super_user, diagram_start_finish_test_results, generate_test_report_gen
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            test_id = diagram_start_finish_test_results["test_id"]
        with allure.step("Получение результата тест кейса"):
            results = []
            test_results = get_testing_results(super_user, test_id).body
            for result in test_results:
                results.append(TestCaseInfo.construct(**result))
            test_case_id = results[0].caseId
            case_info = TestCaseGetFullView.construct(
                **get_testcase_info(super_user, test_case_id).body
            )
        with allure.step("Выгрузка отчёта по тестированию"):
            file_path = generate_test_report_gen.download_testing_report(test_id)
        with allure.step("Проверка, что на второй странице файла отчёта заголовки соответствуют ожидаемым"):
            assert tst_report_validator_titles(file_path, page=2,
                                               out_var_title="out_var",
                                               diagram_exec_status_title="diagram_execute_status")

    @allure.story("Файл тестирования корректно генерируется для диаграммы с примтивными типами")
    @allure.title("Создать диаграмму со входными и выходными примитивными переменными, сгенерировать файл"
                  "тестирования, проверить, что состав переменных совпадает")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    @pytest.mark.save_diagram(True)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_int", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="in_str", varType="in", varDataType=IntValueType.str.value),
         VariableParams(varName="out_int", varType="out", varDataType=IntValueType.str.value),
         VariableParams(varName="out_date", varType="out", varDataType=IntValueType.str.value),
         VariableParams(varName="out_long", varType="out", varDataType=IntValueType.bool.value),
         VariableParams(varName="out_float", varType="out", varDataType=IntValueType.float.value)])
    def test_testfile_correctly_generated_primitive(self, super_user, diagram_constructor, generate_test_file_gen):
        with allure.step("Получение переменных и идентификаторов диаграммы"):
            diagram_id = diagram_constructor["saved_data"].diagramId
            version_id = diagram_constructor["saved_data"].versionId
            in_vars: List[DiagramInOutParameterFullViewDto] = \
                [DiagramInOutParameterFullViewDto.construct(**var) for var in
                 get_filtered_variables(super_user,
                                        version_id,
                                        "входные")]
            out_vars: List[DiagramInOutParameterFullViewDto] = \
                [DiagramInOutParameterFullViewDto.construct(**var) for var in
                 get_filtered_variables(super_user,
                                        version_id,
                                        "выходные")]
        with allure.step("Создание пустого теста"):
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
            create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
        with allure.step("Загрузка файла для тестирования диаграммы и его парсинг"):
            file_path = generate_test_file_gen.generate_and_load_testing_file(
                diagram_version_id=version_id
            )
            testfile_parse_result = file_testing_get_inout_variables(file_path)
            testfile_in_vars = testfile_parse_result["in_variables"]
            testfile_out_vars = testfile_parse_result["out_variables"]

        with allure.step("Проверка, что все входные переменные в файле"):
            assert all(in_var.parameterName in testfile_in_vars for in_var in in_vars) \
                   and len(in_vars) == len(testfile_in_vars)
        with allure.step("Проверка, что все выходные переменные в файле"):
            assert all(out_var.parameterName in testfile_out_vars for out_var in out_vars) \
                   and len(out_vars) == len(testfile_out_vars)

    @allure.story("Файл тестирования корректно генерируется для диаграммы с комплексными типами")
    @allure.title("Создать диаграмму со входными и выходными комплексными переменными, сгенерировать файл"
                  "тестирования, проверить, что состав переменных совпадает")
    @pytest.mark.scenario("DEV-14602")
    @pytest.mark.smoke
    @pytest.mark.save_diagram(True)
    @pytest.mark.variable_data(
        [VariableParams(varName="input_var", varType="in", varDataType=IntValueType.int.value),
         VariableParams(varName="input_rule", varType="in", varDataType=IntValueType.complex_type_rule.value,
                        isComplex=True, isArray=True, isConst=False),
         VariableParams(varName="input_ctype", varType="in", isComplex=True, isArray=True),
         VariableParams(varName="out_rule_result", varType="out", varDataType=IntValueType.complex_type_rule.value,
                        isComplex=True, isArray=True, isConst=False)])
    def test_testfile_correctly_generated_complex(self, super_user, diagram_constructor, generate_test_file_gen):
        with allure.step("Получение переменных и идентификаторов диаграммы"):
            diagram_id = diagram_constructor["saved_data"].diagramId
            version_id = diagram_constructor["saved_data"].versionId
            in_vars: List[DiagramInOutParameterFullViewDto] = \
                [DiagramInOutParameterFullViewDto.construct(**var) for var in
                 get_filtered_variables(super_user,
                                        version_id,
                                        "входные")]
            out_vars: List[DiagramInOutParameterFullViewDto] = \
                [DiagramInOutParameterFullViewDto.construct(**var) for var in
                 get_filtered_variables(super_user,
                                        version_id,
                                        "выходные")]
            in_ctype_vars: List[DiagramInOutParameterFullViewDto] = list(filter(lambda var: var.complexFlag, in_vars))
            out_ctype_vars: List[DiagramInOutParameterFullViewDto] = list(filter(lambda var: var.complexFlag, out_vars))

        with allure.step("Получение атрибутов пользовательских переменных диаграммы"):
            diagram_ctype_vars_with_attributes = dict()
            for var in in_ctype_vars:
                attributes: List[AttributeGetFullView] = \
                    [AttributeGetFullView.construct(**attr) for attr in
                     get_custom_type_attributes(super_user, var.typeId).body]
                # так как в тестовом файле к комплексным переменным добавляется "_" - тоже добавляем его к ключу
                # (остальное обрезается при парсинге тестового файла)
                diagram_ctype_vars_with_attributes["_" + var.parameterName] = [ctype_attr.attributeName for ctype_attr
                                                                               in attributes]

            for var in out_ctype_vars:
                attributes: List[AttributeGetFullView] = \
                    [AttributeGetFullView.construct(**attr) for attr in
                     get_custom_type_attributes(super_user, var.typeId).body]
                # так как в тестовом файле к выходным переменным добавляется "_res_" - тоже добавляем его к ключу
                # (остальное обрезается при парсинге тестового файла)
                diagram_ctype_vars_with_attributes["_res_" + var.parameterName] = [ctype_attr.attributeName for
                                                                                   ctype_attr in
                                                                                   attributes]

        with allure.step("Загрузка файла для тестирования диаграммы и его парсинг"):
            file_path = generate_test_file_gen.generate_and_load_testing_file(
                diagram_version_id=version_id
            )
            testfile_parse_result = file_testing_get_inout_variables(file_path)
            testfile_in_vars = testfile_parse_result["in_variables"]
            testfile_out_vars = testfile_parse_result["out_variables"]
            testfile_ctype_vars_with_attributes = testfile_parse_result["ctype_with_values"]

        with allure.step("Проверка, что все входные переменные пользовательского типа в файле"):
            assert all(in_сtype_var.parameterName in testfile_in_vars for in_сtype_var in in_ctype_vars)
        with allure.step("Проверка, что все выходные переменные пользовательского типа в файле"):
            assert all(out_ctype_var.parameterName in testfile_out_vars for out_ctype_var in out_ctype_vars)
        with allure.step("Проверка, что все атрибуты комплексных переменных присутствуют в тестовом файле"):
            for ctype_name in diagram_ctype_vars_with_attributes.keys():
                assert (all(attr_name in testfile_ctype_vars_with_attributes[ctype_name]
                            for attr_name in diagram_ctype_vars_with_attributes[ctype_name]))

    @allure.story("Тестирование успешно проходит для корректного теста")
    @allure.title("Создать диаграмму со входными и выходными примитивными переменными, сгенерировать файл"
                  "тестирования, проверить, что состав переменных совпадает")
    @pytest.mark.scenario("DEV-12567")
    @pytest.mark.smoke
    @pytest.mark.save_diagram(True)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_float", varType="in_out", varDataType=IntValueType.float.value,
                        isConst=False, varValue="in_out_float"),
         VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value,
                        isConst=False, varValue="in_out_int"),
         VariableParams(varName="in_out_str", varType="in_out", varDataType=IntValueType.str.value,
                        isConst=False, varValue="in_out_str"),
         VariableParams(varName="in_out_date", varType="in_out", varDataType=IntValueType.date.value,
                        isConst=False, varValue="in_out_date"),
         VariableParams(varName="in_out_datetime", varType="in_out", varDataType=IntValueType.dateTime.value,
                        isConst=False, varValue="in_out_datetime"),
         VariableParams(varName="in_out_bool", varType="in_out", varDataType=IntValueType.bool.value,
                        isConst=False, varValue="in_out_bool"),
         VariableParams(varName="in_out_long", varType="in_out", varDataType=IntValueType.long.value,
                        isConst=False, varValue="in_out_long")])
    def test_testfile_fail_works_primitive(self, super_user, diagram_constructor, generate_test_file_gen):
        with allure.step("Получение переменных и идентификаторов диаграммы"):
            diagram_id = diagram_constructor["saved_data"].diagramId
            version_id = diagram_constructor["saved_data"].versionId
            diagram_vars: List[DiagramInOutParameterFullViewDto] = \
                [DiagramInOutParameterFullViewDto.construct(**var) for var in
                 get_filtered_variables(super_user,
                                        version_id, )]
        with allure.step("Загрузка файла для тестирования диаграммы и его парсинг"):
            file_path = generate_test_file_gen.generate_and_load_testing_file(
                diagram_version_id=version_id
            )
            testfile_fill_result = file_testing_generate_test_cases(file_path, diagram_vars,
                                                                    test_to_fail=True)
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
        with allure.step("Создание нового тест-цикла в диаграмме"):
            test_create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
            test_set_id = test_create_result.testId
        with allure.step("Загрузка заполненного файла в тест-цикл диаграммы"):
            send_testing_file(
                super_user,
                test_set_id,
                file=file_path,
            )
        with allure.step("Запуск тест-цикла диаграммы"):
            start_testing(super_user, version_id, body=[str(test_set_id)])
            test_status = None
            for i in range(300):
                test_info = TestInfo.construct(
                    **find_test(super_user, test_set_id).body
                )
                if (
                        test_info.status == Status3.EMERGENCY_STOP
                        or test_info.status == Status3.FAIL
                        or test_info.status == Status3.SUCCESS
                ):
                    test_status = test_info.status
                    break
                time.sleep(1)
        with allure.step("получение реузльтатов тест-цикла"):
            test_results = get_testing_results(super_user, test_set_id).body

        with allure.step("Проверка, что все входные переменные в файле"):
            assert not(all(test_result["caseResult"] for test_result in test_results))

    @allure.story("Тестирование успешно проходит для корректного теста")
    @allure.title("Создать диаграмму со входными и выходными примитивными переменными, сгенерировать файл"
                  "тестирования, проверить, что состав переменных совпадает")
    @pytest.mark.scenario("DEV-12567")
    @pytest.mark.smoke
    @pytest.mark.save_diagram(True)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_float", varType="in_out", varDataType=IntValueType.float.value,
                        isConst=False, varValue="in_out_float"),
         VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.int.value,
                        isConst=False, varValue="in_out_int"),
         VariableParams(varName="in_out_str", varType="in_out", varDataType=IntValueType.str.value,
                        isConst=False, varValue="in_out_str"),
         VariableParams(varName="in_out_date", varType="in_out", varDataType=IntValueType.date.value,
                        isConst=False, varValue="in_out_date"),
         VariableParams(varName="in_out_datetime", varType="in_out", varDataType=IntValueType.dateTime.value,
                        isConst=False, varValue="in_out_datetime"),
         VariableParams(varName="in_out_bool", varType="in_out", varDataType=IntValueType.bool.value,
                        isConst=False, varValue="in_out_bool"),
         VariableParams(varName="in_out_long", varType="in_out", varDataType=IntValueType.long.value,
                        isConst=False, varValue="in_out_long")])
    def test_testfile_empty_values_works_primitive(self, super_user, diagram_constructor, generate_test_file_gen):
        with allure.step("Получение переменных и идентификаторов диаграммы"):
            diagram_id = diagram_constructor["saved_data"].diagramId
            version_id = diagram_constructor["saved_data"].versionId
            diagram_vars: List[DiagramInOutParameterFullViewDto] = \
                [DiagramInOutParameterFullViewDto.construct(**var) for var in
                 get_filtered_variables(super_user,
                                        version_id)]
            variable_names = [d_var.parameterName for d_var in diagram_vars]
            variables_with_empty_values = {variable_name: None
                                           for variable_name
                                           in variable_names}
        with allure.step("Загрузка файла для тестирования диаграммы и его парсинг"):
            file_path = generate_test_file_gen.generate_and_load_testing_file(
                diagram_version_id=version_id
            )
            testfile_fill_result = file_testing_generate_test_cases(file_path, diagram_vars,
                                                                    custom_values=variables_with_empty_values)
            empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
        with allure.step("Создание нового тест-цикла в диаграмме"):
            test_create_result = EmptyTestDto(
                **create_empty_test(super_user, body=empty_test).body
            )
            test_set_id = test_create_result.testId
        with allure.step("Загрузка заполненного файла в тест-цикл диаграммы"):
            send_testing_file(
                super_user,
                test_set_id,
                file=file_path,
            )
        with allure.step("Запуск тест-цикла диаграммы"):
            start_testing(super_user, version_id, body=[str(test_set_id)])
            test_status = None
            for i in range(300):
                test_info = TestInfo.construct(
                    **find_test(super_user, test_set_id).body
                )
                if (
                        test_info.status == Status3.EMERGENCY_STOP
                        or test_info.status == Status3.FAIL
                        or test_info.status == Status3.SUCCESS
                ):
                    test_status = test_info.status
                    break
                time.sleep(1)
        with allure.step("получение реузльтатов тест-цикла"):
            test_results = get_testing_results(super_user, test_set_id).body

        with allure.step("Проверка, что все входные переменные в файле"):
            assert len(test_results) > 0
            assert test_status == Status3.SUCCESS

# TODO: написать тесты для файлов с комплексными типами, добавить переменную типа время в тесты
