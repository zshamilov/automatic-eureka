import time

import allure
import pytest
from playwright.sync_api import expect

from common.generators import generate_string
from products.Decision.e2e.framework.actions import wait_for_stable, pick_from_dropdown_menu
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.modal_wndows.node_calc import CalcConfigurationModal
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.shared_po.add_new_element_modal import NewElementModal
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.e2e.framework.locators.shared_po.expression_editor_modal import ExpressionEditorModal
from products.Decision.framework.model import DiagramViewDto
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.utilities.custom_models import VariableParams, IntValueType, StrValueType
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct


@allure.epic("Расчёт переменных")
@allure.feature("Расчёт переменных")
class TestNodeCalc:
    @allure.story("Узел рассчёт переменной")
    @allure.title('Развёртывание диаграммы с узлом рассчёт переменных, переменные всех примитивных типов')
    @pytest.mark.variable_data([VariableParams(varName="int_v", varType="in_out", varDataType=IntValueType.int.value,
                                               isConst=False, varValue="int_v"),
                                VariableParams(varName="double_v", varType="in_out",
                                               varDataType=IntValueType.float.value,
                                               isConst=False, varValue="double_v"),
                                VariableParams(varName="str_v", varType="in_out", varDataType=IntValueType.str.value,
                                               isConst=False, varValue="str_v"),
                                VariableParams(varName="date_v", varType="in_out", varDataType=IntValueType.date.value,
                                               isConst=False, varValue="date_v"),
                                VariableParams(varName="bool_v", varType="in_out", varDataType=IntValueType.bool.value,
                                               isConst=False, varValue="bool_v"),
                                VariableParams(varName="date_time_v", varType="in_out",
                                               varDataType=IntValueType.dateTime.value, isConst=False,
                                               varValue="date_time_v"),
                                VariableParams(varName="time_v", varType="in_out", varDataType=IntValueType.time.value,
                                               isConst=False, varValue="time_v"),
                                VariableParams(varName="long_v", varType="in_out", varDataType=IntValueType.long.value,
                                               isConst=False, varValue="long_v")])
    @pytest.mark.nodes(["расчет переменной"])
    @pytest.mark.save_diagram(True)
    def test_node_calc(self, super_user, create_dict_gen,
                       diagram_constructor, faker, page, allure_step):
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        calc_modal = CalcConfigurationModal(page=page)
        new_element_modal = NewElementModal(page=page)
        expression_editor = ExpressionEditorModal(page=page)
        deploy_page = DeployPage(page=page)
        main_page = MainPage(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="4",
                                         dict_value_display_name="")
            dict_name = "ag_a_test_dict" + generate_string()
            custom_attr = dict_construct(
                dict_name=dict_name,
                dict_value_type_id="1",
                values=[value])
            create_dict_gen.create_dict(dict_body=custom_attr)
        with allure_step(f'Открытие диаграммы'):
            main_page.nav_bar_options(option_name="Разработка").click()
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step('Открытие узла расчёта'):
            wait_for_stable(diagram_page.diagram_name_header)
            buttons_page.zoom_buttons("отдалить").click(click_count=4)
            diagram_page.node_on_the_board("расчет переменной").click(click_count=2)
        with allure_step(
                'Задание целочисленной переменной - создание переменной и маппинг переменной диаграммы чере EE'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("int_n_v2")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.int.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.int.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="int_n_v2")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="int_n_v2").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.add_element_btn.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="int_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="int_v").check()
            new_element_modal.button_by_text('Добавить').last.click()
            new_element_modal.button_by_text('Добавить').click()
        # with allure_step('Задание целочисленной переменной - создание переменной значение через справочник'):
        #     expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
        #         timeout=20000)
        #     new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
        #     new_element_modal.button_by_cell_value(cell_value="").first.click()
        #     new_element_modal.new_el_modal_add_btn.click()
        #     new_element_modal.field("Наименование элемента").fill("int_dict_v")
        #     expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
        #     new_element_modal.field("Тип элемента").click(force=True)
        #     new_element_modal.field("Тип элемента").fill(StrValueType.int.value)
        #     new_element_modal.element_from_dropdown(text=StrValueType.int.value).click(force=True)
        #     new_element_modal.field("Выбрать из списка флаг").click()
        #     new_element_modal.field("Выбрать из списка").click(force=True)
        #     new_element_modal.element_from_dropdown(text=dict_name).click(force=True)
        #     new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
        #     expect(new_element_modal.value_checkbox_by_row_key(name="int_dict_v")).to_be_enabled()
        #     new_element_modal.value_checkbox_by_row_key(name="int_dict_v").check()
        #     new_element_modal.button_by_text('Добавить').click()
        #     calc_modal.vars_table(var_name="int_dict_v", field="Значение").click(force=True)
        #     new_element_modal.element_from_dropdown(text="4").click()
        with allure_step(
                'Задание целочисленной переменной - маппинг значения руками'):
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="int_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="int_v").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.field_by_cell_value(cell_value="").fill("25")
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step('Задание дробной переменной - маппинг значения руками'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="double_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="double_v").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.field_by_cell_value(cell_value="").fill("25.2")
        with allure_step(
                'Задание дробной переменной - создание переменной и маппинг переменной диаграммы чере EE'):
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("double_n_v1")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.float.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.float.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="double_n_v1")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="double_n_v1").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.add_element_btn.click()
            new_element_modal.value_checkbox_by_row_key(name="double_v").check()
            new_element_modal.button_by_text('Добавить').last.click()
            new_element_modal.button_by_text('Добавить').click()
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step(
                'Задание дробной переменной - создание переменной и маппинг переменной диаграммы чере EE через функцию'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("double_n_v2")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.float.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.float.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="double_n_v2")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="double_n_v2").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.text_area.fill("exp($int_v)")
            new_element_modal.button_by_text('Добавить').click()
        with allure_step('Задание строковой переменной - маппинг значения руками'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="str_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="str_v").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.field_by_cell_value(cell_value="").fill("'some_string'")
        with allure_step(
                'Задание строковой переменной - создание переменной и маппинг переменной диаграммы чере EE'):
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("str_n_v1")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.str.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.str.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="str_n_v1")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="str_n_v1").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.add_element_btn.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="str_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="str_v").check()
            new_element_modal.button_by_text('Добавить').last.click()
            new_element_modal.button_by_text('Добавить').click()
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
            # Activate date time vars
            # expect(new_element_modal.button_by_modal_name_number("Список атрибутов", 1)).to_be_visible(timeout=20000)
            # new_element_modal.button_by_modal_name_number("Список атрибутов", 1).click()
            # new_element_modal.button_by_cell_value(cell_value="").first.click()
            # new_element_modal.new_el_modal_add_btn.click()
            # new_element_modal.field("Наименование элемента").fill("date_time_n_v2")
            # expect(new_element_modal.field("Тип элемента")).to_be_editable(timeout=20000)
            # new_element_modal.field("Тип элемента").click()
            # new_element_modal.field("Тип элемента").fill(StrValueType.dateTime.value)
            # page.keyboard.press("Enter")
            # new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            # expect(new_element_modal.value_checkbox_by_row_key(name="date_time_n_v2")).to_be_enabled()
            # new_element_modal.value_checkbox_by_row_key(name="date_time_n_v2").check()
            # new_element_modal.button_by_text('Добавить').click()
            # new_element_modal.button_by_cell_value(cell_value="").click()
            # expression_editor.text_area.fill("localTime()")
            # new_element_modal.button_by_text('Добавить').click()
            # wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step(
                'Задание дата_время переменной - создание переменной и маппинг переменной диаграммы чере EE'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("date_time_n_v1")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.dateTime.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.dateTime.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="date_time_n_v1")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="date_time_n_v1").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.add_element_btn.click()
            new_element_modal.value_checkbox_by_row_key(name="date_time_v").check()
            new_element_modal.button_by_text('Добавить').last.click()
            new_element_modal.button_by_text('Добавить').click()
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step('Задание строковой переменной - маппинг значения руками'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="bool_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="bool_v").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.field_by_cell_value(cell_value="").fill("true")
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step(
                'Задание логической переменной - создание переменной и маппинг переменной диаграммы чере EE'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("bool_n_v1")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.bool.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.bool.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="bool_n_v1")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="bool_n_v1").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.add_element_btn.click()
            new_element_modal.value_checkbox_by_row_key(name="bool_v").check()
            new_element_modal.button_by_text('Добавить').last.click()
            new_element_modal.button_by_text('Добавить').click()
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step('Задание дата переменной - маппинг значения руками'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="date_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="date_v").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.field_by_cell_value(cell_value="").fill("'2023-07-03'")
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step(
                'Задание дата переменной - создание переменной и маппинг переменной диаграммы чере EE'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("date_n_v1")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.date.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.date.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="date_n_v1")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="date_n_v1").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.add_element_btn.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="date_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="date_v").check()
            new_element_modal.button_by_text('Добавить').last.click()
            new_element_modal.button_by_text('Добавить').click()
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step('Задание время переменной - маппинг значения руками'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="time_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="time_v").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.field_by_cell_value(cell_value="").fill("'20:52:00'")
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step(
                'Задание время переменной - создание переменной и маппинг переменной диаграммы чере EE'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            new_element_modal.new_el_modal_add_btn.click()
            new_element_modal.field("Наименование элемента").fill("time_n_v1")
            expect(new_element_modal.field("Тип элемента")).to_be_visible(timeout=20000)
            new_element_modal.field("Тип элемента").click(force=True)
            new_element_modal.field("Тип элемента").fill(StrValueType.time.value, force=True)
            new_element_modal.element_from_dropdown(text=StrValueType.time.value).click(force=True)
            new_element_modal.add_el_modal_btn(button_name='Сохранить').click()
            expect(new_element_modal.value_checkbox_by_row_key(name="time_n_v1")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="time_n_v1").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.button_by_cell_value(cell_value="").click()
            expression_editor.add_element_btn.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="time_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="time_v").check()
            new_element_modal.button_by_text('Добавить').last.click()
            new_element_modal.button_by_text('Добавить').click()
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step('Задание long переменной - маппинг значения руками'):
            expect(new_element_modal.button_by_modal_name_number("Список атрибутов", number=1)).to_be_visible(
                timeout=20000)
            new_element_modal.button_by_modal_name_number("Список атрибутов", number=1).click()
            new_element_modal.button_by_cell_value(cell_value="").first.click()
            expect(new_element_modal.value_checkbox_by_row_key(name="long_v")).to_be_enabled()
            new_element_modal.value_checkbox_by_row_key(name="long_v").check()
            new_element_modal.button_by_text('Добавить').click()
            new_element_modal.field_by_cell_value(cell_value="").fill("100000000000000000")
            wait_for_stable(new_element_modal.modal_window(modal_window_name="расчет переменной"))
        with allure_step('Сохранение узла'):
            with page.expect_response("**/nodes/**") as response_info:
                new_element_modal.button_by_text(text="Сохранить").click()
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
                expect(new_element_modal.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                new_element_modal.button_by_text(text="Далее").click()
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
            wait_for_stable(new_element_modal.modal_window("Параметры развертывания диаграмм"))
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
