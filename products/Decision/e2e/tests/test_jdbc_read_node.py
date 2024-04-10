import allure
import pytest
from playwright.sync_api import expect

from products.Decision.e2e.framework.actions import *
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.modal_wndows.node_read import NodeReadPage
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.db_framework import db_model
from products.Decision.framework.model import DiagramViewDto, DataProviderGetFullView
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.utilities.custom_models import VariableParams, AttrInfo, IntValueType


@allure.epic("Чтение данных")
@allure.feature("Чтение данных")
class TestNodeRead:
    @allure.story("Узел чтения данных")
    @allure.title('Развёртывание диаграммы с узлом чтения, комплексная переменная с атрибутами всех типов')
    @allure.issue("DEV-13155")
    @pytest.mark.table_name(db_model.read_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_cmplx_all_prim", varType="in_out", isComplex=True,
                                               isConst=False,
                                               cmplxAttrInfo=[AttrInfo(attrName="float_attr",
                                                                       intAttrType=IntValueType.float),
                                                              AttrInfo(attrName="int_attr",
                                                                       intAttrType=IntValueType.int),
                                                              AttrInfo(attrName="str_attr",
                                                                       intAttrType=IntValueType.str),
                                                              AttrInfo(attrName="date_attr",
                                                                       intAttrType=IntValueType.date),
                                                              AttrInfo(attrName="bool_attr",
                                                                       intAttrType=IntValueType.bool),
                                                              AttrInfo(attrName="time_attr",
                                                                       intAttrType=IntValueType.time),
                                                              AttrInfo(attrName="datetime_attr",
                                                                       intAttrType=IntValueType.dateTime)])])
    @pytest.mark.nodes(["чтение"])
    @pytest.mark.save_diagram(True)
    def test_node_read(self, super_user, provider_constructor,
                       diagram_constructor, create_db_all_tables_and_scheme, faker, page, allure_step):
        table_name = provider_constructor["table_name"]
        provider: DataProviderGetFullView = provider_constructor["provider_info"]
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        node_read_page = NodeReadPage(page=page)
        deploy_page = DeployPage(page=page)
        main_page = MainPage(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        with allure_step(f'Открытие диаграммы'):
            main_page.nav_bar_options(option_name="Разработка").click()
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step('Открытие узла "Чтение данных"'):
            wait_for_stable(diagram_page.diagram_name_header)
            diagram_page.node_on_the_board("чтение").click(click_count=2)
        with allure_step("Добавление таблицы БД"):
            wait_for_stable(node_read_page.modal_window("чтение"))
            node_read_page.add_dataprovider_btn.click()
            wait_for_stable(node_read_page.modal_window("Выбор источника данных"))
            #node_read_page.diagram_var_content_button(var_name=str(provider.sourceId)).click()
            node_read_page.get_value_field_by_placeholder("Поиск...").fill(provider.sourceName)
            checkbox_check_action(node_read_page.get_checkbox_by_row_name(provider.sourceName).first)
            with allure_step("Подтверждение выбора"):
                node_read_page.modal_window("Выбор источника данных").locator(buttons_page.ok_btn.last).click()
                node_read_page.add_table_btn.click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name(table_name).first)
                node_read_page.confirm_table_btn.click()
        with allure_step("Заполнение конструкции SQL-запроса"):
            with allure_step("Развертывание списка переменных"):
                node_read_page.expand_table_columns.click()
            with allure_step("Перетаскивание переменной типа bool и маппинг"):
                node_read_page.textarea.clear()
                node_read_page.textarea.fill("select")
                node_read_page.option_by_text("bool_val").drag_to(node_read_page.textarea)
                node_read_page.button_by_cell_value("").last.click()
                wait_for_stable(node_read_page.modal_window("Добавить элемент"))
                node_read_page.modal_window("Добавить элемент").locator(node_read_page.roll_list.first).click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name("bool_attr"))
                node_read_page.modal_window("Добавить элемент").locator(buttons_page.add_btn).click()
            with allure_step("Перетаскивание переменной типа double и маппинг"):
                text = node_read_page.textarea.input_value()
                node_read_page.textarea.clear()
                node_read_page.textarea.fill(text + ",")
                node_read_page.option_by_text("double_val").drag_to(node_read_page.textarea)
                node_read_page.button_by_cell_value("").last.click()
                wait_for_stable(node_read_page.modal_window("Добавить элемент"))
                node_read_page.modal_window("Добавить элемент").locator(node_read_page.roll_list.first).click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name("float_attr"))
                node_read_page.modal_window("Добавить элемент").locator(buttons_page.add_btn).click()
            with allure_step("Перетаскивание переменной типа date_time и маппинг"):
                text = node_read_page.textarea.input_value()
                node_read_page.textarea.clear()
                node_read_page.textarea.fill(text + ",")
                node_read_page.option_by_text("date_time_val").drag_to(node_read_page.textarea)
                node_read_page.button_by_cell_value("").last.click()
                wait_for_stable(node_read_page.modal_window("Добавить элемент"))
                node_read_page.modal_window("Добавить элемент").locator(node_read_page.roll_list.first).click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name("datetime_attr"))
                node_read_page.modal_window("Добавить элемент").locator(buttons_page.add_btn).click()
            with allure_step("Перетаскивание переменной типа int и маппинг"):
                text = node_read_page.textarea.input_value()
                node_read_page.textarea.clear()
                node_read_page.textarea.fill(text + ",")
                node_read_page.option_by_text("int_val").drag_to(node_read_page.textarea)
                node_read_page.button_by_cell_value("").last.click()
                wait_for_stable(node_read_page.modal_window("Добавить элемент"))
                node_read_page.modal_window("Добавить элемент").locator(node_read_page.roll_list.first).click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name("int_attr"))
                node_read_page.modal_window("Добавить элемент").locator(buttons_page.add_btn).click()
            with allure_step("Перетаскивание переменной типа date и маппинг"):
                text = node_read_page.textarea.input_value()
                node_read_page.textarea.clear()
                node_read_page.textarea.fill(text + ",\n")
                node_read_page.option_by_text("date_val").drag_to(node_read_page.textarea)
                node_read_page.button_by_cell_value("").last.click()
                wait_for_stable(node_read_page.modal_window("Добавить элемент"))
                node_read_page.modal_window("Добавить элемент").locator(node_read_page.roll_list.first).click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name("date_attr"))
                node_read_page.modal_window("Добавить элемент").locator(buttons_page.add_btn).click()
            with allure_step("Перетаскивание переменной типа time и маппинг"):
                text = node_read_page.textarea.input_value()
                node_read_page.textarea.clear()
                node_read_page.textarea.fill(text + ",")
                node_read_page.option_by_text("time_val").drag_to(node_read_page.textarea)
                node_read_page.button_by_cell_value("").last.click()
                wait_for_stable(node_read_page.modal_window("Добавить элемент"))
                node_read_page.modal_window("Добавить элемент").locator(node_read_page.roll_list.first).click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name("time_attr").first)
                node_read_page.modal_window("Добавить элемент").locator(buttons_page.add_btn).click()
            with allure_step("Перетаскивание переменной типа str и маппинг"):
                text = node_read_page.textarea.input_value()
                node_read_page.textarea.clear()
                node_read_page.textarea.fill(text + ",")
                node_read_page.option_by_text("str_val").drag_to(node_read_page.textarea)
                node_read_page.button_by_cell_value("").last.click()
                wait_for_stable(node_read_page.modal_window("Добавить элемент"))
                node_read_page.modal_window("Добавить элемент").locator(node_read_page.roll_list.first).click()
                checkbox_check_action(node_read_page.get_checkbox_by_row_name("str_attr"))
                node_read_page.modal_window("Добавить элемент").locator(buttons_page.add_btn).click()
            with allure_step("Заполнение секции from SQL-запроса"):
                text = node_read_page.textarea.input_value()
                node_read_page.textarea.clear()
                node_read_page.textarea.fill(text + f"\nfrom {table_name}\nwhere int_val <> 0")
            with allure_step("Проверка запроса"):
                node_read_page.check_query.click()
                expect(node_read_page.option_by_text("Валидация прошла успешно")).to_be_visible()
                buttons_page.close_btn.click()
            with allure_step("Сохранение настроенного узла"):
                buttons_page.save_btn.click()
            with allure.step('Сохранение узла завершения'):
                wait_for_stable(diagram_page.diagram_name_header)
                diagram_page.node_on_the_board("Завершение").click(click_count=2)
                with page.expect_response("**/nodes/**") as response_info:
                    buttons_page.save_btn.click()
                assert response_info.value.status == 200
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
                expect(node_read_page.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                node_read_page.button_by_text(text="Далее").click()
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
            wait_for_stable(node_read_page.modal_window("Параметры развертывания диаграмм"))
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
