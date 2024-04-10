from time import sleep

import allure
import pytest

from playwright.sync_api import expect
from products.Decision.e2e.framework.actions import *
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.modal_wndows.node_read import NodeReadPage
from products.Decision.e2e.framework.locators.modal_wndows.node_jdbc_write_modal import InsertConfigurationModal
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.pages.variables_page import VariablesConfigurationModal
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.model import DiagramViewDto
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Начало/Завершение")
@allure.feature("Начало/Завершение")
class TestNodeStartFinish:
    @allure.story("Узел начало завершение")
    @allure.title('Развёртывание диаграммы с узлами начало завершение, переменные всех примитивных типов')
    @pytest.mark.variable_data([VariableParams(varName="int_v", varType="in_out", varDataType=IntValueType.int.value,
                                               isConst=False, varValue="int_v"),
                                VariableParams(varName="double_v", varType="in_out",
                                               varDataType=IntValueType.float.value, isConst=False, varValue="double_v"),
                                VariableParams(varName="str_v", varType="in_out", varDataType=IntValueType.str.value,
                                               isConst=False, varValue="str_v"),
                                VariableParams(varName="date_v", varType="in_out", varDataType=IntValueType.date.value,
                                               isConst=False, varValue="date_v"),
                                VariableParams(varName="bool_v", varType="in_out", varDataType=IntValueType.bool.value,
                                               isConst=False, varValue="bool_v"),
                                VariableParams(varName="date_time_v", varType="in_out",
                                               varDataType=IntValueType.dateTime.value,
                                               isConst=False, varValue="date_time_v"),
                                VariableParams(varName="time_v", varType="in_out", varDataType=IntValueType.time.value,
                                               isConst=False, varValue="time_v"),
                                VariableParams(varName="long_v", varType="in_out",
                                               varDataType=IntValueType.long.value,
                                               isConst=False, varValue="long_v")])
    @pytest.mark.save_diagram(True)
    def test_node_start_finish(self, super_user,
                               diagram_constructor, faker, page, allure_step):
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        deploy_page = DeployPage(page=page)
        main_page = MainPage(page=page)
        read_page = NodeReadPage(page=page)
        write_page = InsertConfigurationModal(page=page)
        variable_page = VariablesConfigurationModal(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        with allure_step('Открытие диаграммы'):
            main_page.nav_bar_options(option_name="Разработка").click()
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step("Переход во вкладку 'Переменные'"):
            read_page.option_by_text("Переменные").click()
            with allure_step("Установка аварийного значения"):
                variable_page.reserved_value_by_row_content("bool_v").click()
                page.locator("textarea").fill("True")
                variable_page.modal_window("bool_v").locator(buttons_page.add_btn.last).click()
                variable_page.reserved_value_by_row_content("time_v").click()
                page.locator("textarea").fill("'23:00:54'")
                variable_page.modal_window("time_v").locator(buttons_page.add_btn.last).click()
                variable_page.reserved_value_by_row_content("int_v").click()
                page.locator("textarea").fill("23")
                variable_page.modal_window("int_v").locator(buttons_page.add_btn.last).click()
                variable_page.reserved_value_by_row_content("date_v").click()
                page.locator("textarea").fill("'2023-07-01'")
                variable_page.modal_window("date_v").locator(buttons_page.add_btn.last).click()
                variable_page.reserved_value_by_row_content("date_time_v").click()
                page.locator("textarea").fill("'2023-07-01 01:01.000'")
                variable_page.modal_window("date_time_v").locator(buttons_page.add_btn.last).click()
                variable_page.reserved_value_by_row_content("double_v").click()
                page.locator("textarea").fill("23.0")
                variable_page.modal_window("double_v").locator(buttons_page.add_btn.last).click()
                variable_page.reserved_value_by_row_content("str_v").click()
                page.locator("textarea").fill("'23'")
                variable_page.modal_window("str_v").locator(buttons_page.add_btn.last).click()
                variable_page.reserved_value_by_row_content("long_v").click()
                page.locator("textarea").fill("1000000000000000000")
                variable_page.modal_window("long_v").locator(buttons_page.add_btn.last).click()
        with allure_step("Переход во вкладку 'Диаграмма'"):
            read_page.option_by_text("Диаграмма").click()
        with allure_step('Открытие узла "Начало"'):
            wait_for_stable(diagram_page.diagram_name_header)
            buttons_page.zoom_buttons("отдалить").click(click_count=4)
            diagram_page.node_on_the_board("Начало").click(click_count=2)
            wait_for_stable(read_page.modal_window("Начало"))
            with allure_step("Проверка наличия переменных и их типов"):
                expect(read_page.get_row_by_its_content("bool_v")).to_contain_text("Логический")
                expect(read_page.get_row_by_its_content("time_v")).to_contain_text("Время")
                expect(read_page.get_row_by_its_content("int_v")).to_contain_text("Целочисленный (INT)")
                expect(read_page.get_row_by_its_content("date_v")).to_contain_text("Дата")
                expect(read_page.get_row_by_its_content("date_time_v")).to_contain_text("Дата_время")
                expect(read_page.get_row_by_its_content("double_v")).to_contain_text("Дробный")
                expect(read_page.get_row_by_its_content("str_v")).to_contain_text("Строковый")
                expect(read_page.get_row_by_its_content("long_v")).to_contain_text("Целочисленный (LONG)")
            with allure_step('Выход из узла "Начало"'):
                buttons_page.reject_btn.click()
        with allure_step('Открытие узла "завершение"'):
            wait_for_stable(diagram_page.diagram_name_header)
            diagram_page.node_on_the_board("Завершение").click(click_count=2)
            with allure_step("Проверка наличия переменных и их типов"):
                expect(read_page.get_row_by_its_content("bool_v")).to_contain_text("Логический")
                expect(read_page.get_row_by_its_content("bool_v")).to_contain_text("True")
                expect(read_page.get_row_by_its_content("time_v")).to_contain_text("Время")
                expect(read_page.get_row_by_its_content("time_v")).to_contain_text("23:00:54")
                expect(read_page.get_row_by_its_content("int_v")).to_contain_text("Целочисленный (INT)")
                expect(read_page.get_row_by_its_content("int_v")).to_contain_text("23")
                expect(read_page.get_row_by_its_content("date_v")).to_contain_text("Дата")
                expect(read_page.get_row_by_its_content("date_v")).to_contain_text("2023-07-01")
                expect(read_page.get_row_by_its_content("date_time_v")).to_contain_text("Дата_время")
                expect(read_page.get_row_by_its_content("date_time_v")).to_contain_text("2023-07-01 01:01.000")
                expect(read_page.get_row_by_its_content("double_v")).to_contain_text("Дробный")
                expect(read_page.get_row_by_its_content("double_v")).to_contain_text("23.0")
                expect(read_page.get_row_by_its_content("str_v")).to_contain_text("Строковый")
                expect(read_page.get_row_by_its_content("str_v")).to_contain_text("23")
                expect(read_page.get_row_by_its_content("long_v")).to_contain_text("Целочисленный (LONG)")
                expect(read_page.get_row_by_its_content("long_v")).to_contain_text("1000000000000000000")
            with allure_step("Выбор опции 'Null значение'"):
                checkbox_check_action(write_page.null_value_checkbox("long_v"))
            with allure_step("Проверка, что поле для установки значения задизейблино"):
                expect(write_page.input_button_by_content("long_v")).to_be_disabled()
            with allure_step("Сохранение узла 'Завершение'"):
                buttons_page.save_btn.click()
        with allure_step('Сохранение обновлённой диаграммы'):
            with page.expect_response("**/diagrams") as response_info:
                diagram_page.save_btn.click()
            assert response_info.value.status == 201
            wait_for_stable(diagram_page.diagram_name_header)
        with allure_step('Отправка диаграммы на развёртование, тип REALTIME'):
            expect(diagram_page.submit_btn).to_be_enabled(timeout=20000)
            diagram_page.submit_btn.click()
            sleep(2)
            with page.expect_response("**/submit") as response_info:
                expect(read_page.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                read_page.button_by_text(text="Далее").click()
            assert response_info.value.status == 201
        with allure_step('Ожидание, что диаграмма успешно отправлена на развёртование'):
            expect(diagram_page.get_success_modal(diagram_name=diagram_data.objectName)) \
                .to_contain_text(f"Диаграмма {diagram_data.objectName} была успешно отправлена на развертывание",
                                 timeout=20000)
        with allure_step('Переход на вкладку администрирование, к списку деплоев'):
            main_page.nav_bar_options(option_name="Администрирование").click()
            main_page.development_nav_bar_options(option_name="Развертывание диаграмм").click()
            deploy_id = find_deploy_id(super_user, diagram_data.objectName, diagram_data.diagramId)
        with allure_step('Развёртование диаграммы'):
            deploy_page.deploy_checkbox_deploy_id(deploy_id=deploy_id).click()
            deploy_page.deploy_btn.click()
            wait_for_stable(read_page.modal_window("Параметры развертывания диаграмм"))
            deploy_config_modal.diagram_selector.click(force=True)
            deploy_config_modal.element_from_dropdown(text=diagram_data.objectName).click()
            expect(buttons_page.deploy_btn.last).to_be_enabled(timeout=20000)
            buttons_page.deploy_btn.last.click()
        with allure_step("Идентификация, что диаграмма находится в процессе развертывания"):
            expect(deploy_page.deploy_status_by_deploy_id(deploy_id=deploy_id)).to_have_text("На развертывании",
                                                                                             timeout=20000)
        with allure_step("Идентификация, что развертывание произошло успешно"):
            expect(deploy_page.deploy_status_by_deploy_id(deploy_id=deploy_id),
                   "ожидание деплоя").to_have_text("Развернута",
                                                   timeout=360000)
