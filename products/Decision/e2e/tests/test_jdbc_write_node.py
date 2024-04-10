import time

import allure
import pytest
from playwright.sync_api import expect

from products.Decision.e2e.framework.actions import wait_for_stable, checkbox_check_action
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.modal_wndows.node_jdbc_write_modal import InsertConfigurationModal
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.model import DiagramInOutParameterFullViewDto, DiagramViewDto, DataProviderGetFullView
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.utilities.custom_models import VariableParams, AttrInfo, IntValueType


@allure.epic("Сохранение данных")
@allure.feature("Сохранение данных")
class TestNodeJdbcWrite:
    @allure.story("Узел записи данных")
    @allure.title('Развёртывание диаграммы с узлом записи, комплексная входная переменная с атрибутами всех типов, '
                  'вставка и обновление данных через ручной ввод и маппинг атрибутов')
    @allure.issue("DEV-14216")
    @pytest.mark.variable_data([VariableParams(varName="out_int", varType="out", varDataType=1),
                                VariableParams(varName="in_cmplx", varType="in", isComplex=True,
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
    @pytest.mark.nodes(["запись"])
    @pytest.mark.save_diagram(True)
    def test_node_jdbc_write(self, super_user, create_data_provider_gen, create_db_all_tables_and_scheme,
                             diagram_constructor, faker, page, allure_step):
        table_name = "insert_node_e2e_table"
        provider: DataProviderGetFullView = create_data_provider_gen.create_postgress_provider()
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        input_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        deploy_page = DeployPage(page=page)
        insert_node_modal = InsertConfigurationModal(page=page)
        main_page = MainPage(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        with allure_step(f'Открытие диаграммы'):
            main_page.nav_bar_options(option_name="Разработка").click()
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step('Открытие узла записи для его настройки'):
            wait_for_stable(diagram_page.diagram_name_header)
            diagram_page.node_on_the_board(node_name="запись").click(click_count=2)
        with allure_step('Выбор формата работы узла сохранения данных'):
            insert_node_modal.insert_type_dropdown.click()
            insert_node_modal.insert_type("Вставка и обновление данных").click()
            wait_for_stable(insert_node_modal.modal_window(modal_window_name="запись"))
        with allure_step('Выбор таблицы из БД'):
            insert_node_modal.provider_select_btn.click()
            insert_node_modal.get_value_field_by_placeholder("Поиск...").fill(provider.sourceName)
            checkbox_check_action(insert_node_modal.get_checkbox_by_row_name(provider.sourceName).first)
            insert_node_modal.modal_window("Выбор источника данных").locator(buttons_page.ok_btn.last).click()
            insert_node_modal.table_select_button.click()
            checkbox_check_action(insert_node_modal.get_checkbox_by_row_name(table_name).first)
            insert_node_modal.confirm_table_btn.click()
        with allure_step('Редактирование записи в БД через маппинг атрибута переменной комплексного типа'):
            # insert_node_modal.button_by_modal_name_number(name='Условия отбора записей в БД', number=2).click()
            # insert_node_modal.value_checkbox_by_name(name="int_val").check()
            # insert_node_modal.confirm_button.click()
            insert_node_modal.button_by_modal_name_and_cell_value(modal_name='Условия отбора записей в БД',
                                                                  cell_value="").click()
            insert_node_modal.diagram_var_content_button(var_name=input_var.parameterName).click()
            insert_node_modal.select_value_checkbox(value="in_cmplx.int_attr").click()
            insert_node_modal.button_by_text(text="Добавить").click()
        # with allure_step('Редактирование записи в БД через ввод значения'):
        #     insert_node_modal.add_button_by_modal_name(name='Условия отбора записей в БД').click()
        #     insert_node_modal.value_checkbox_by_name(name="double_val").check()
        #     insert_node_modal.confirm_button.click()
        #     insert_node_modal.field_by_cell_value(cell_value="").fill("25.2")
        with allure_step('Вставка записи в БД через маппинг атрибута переменной комплексного типа'):
            insert_node_modal.button_by_modal_name_and_cell_value(modal_name='Обновляемые атрибуты в БД',
                                                                  cell_value="").click()
            insert_node_modal.diagram_var_content_button(var_name=input_var.parameterName).click()
            insert_node_modal.select_value_checkbox(value="in_cmplx.bool_attr").click()
            insert_node_modal.button_by_text(text="Добавить").click()
        # with allure_step('Вставка записи в БД через ввод значения'):
        #     insert_node_modal.add_button_by_modal_name(name='Атрибуты добавляемой записи в БД').click()
        #     insert_node_modal.value_checkbox_by_name(name="str_val").check()
        #     insert_node_modal.confirm_button.click()
        #     insert_node_modal.field_by_cell_value(cell_value="").fill("'some_string'")
        with allure_step('Сохранение узла'):
            with page.expect_response("**/nodes/**") as response_info:
                insert_node_modal.button_by_text(text="Сохранить").click()
            assert response_info.value.status == 200
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
            time.sleep(2)
            with page.expect_response("**/submit") as response_info:
                expect(insert_node_modal.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                insert_node_modal.button_by_text(text="Далее").click()
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
            wait_for_stable(insert_node_modal.modal_window("Параметры развертывания диаграмм"))
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
