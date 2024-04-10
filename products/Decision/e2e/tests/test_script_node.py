import time
import allure
import pytest
from faker import Faker

from playwright.sync_api import expect

from common.generators import generate_string
from products.Decision.e2e.framework.actions import *
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.custom_code_page import CustomCodePage
from products.Decision.e2e.framework.locators.modal_wndows.node_custom_code import CustomCodeConfigurationModal
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.model import DiagramViewDto
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.utilities.custom_models import VariableParams, IntValueType, AttrInfo

faker = Faker()


@allure.epic("Кастомный код")
@allure.feature("Кастомный код")
class TestNodeScript:
    @allure.story("Узел кастомный код")
    @allure.title('Развёртывание диаграммы с узлом кастомный код, переменные всех примитивных типовб комплексные и '
                  'массивы')
    @allure.issue("DEV-14607")
    @pytest.mark.variable_data(
        [VariableParams(varName="int_v_arr", varType="in_out", varDataType=IntValueType.int.value,
                        isArray=True, isConst=False, varValue="int_v_arr"),
         VariableParams(varName="int_v", varType="in_out", varDataType=IntValueType.int.value,
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
                        isConst=False, varValue="long_v"),
         VariableParams(varName="cmplx", varType="in_out", isComplex=True,
                        isConst=False,
                        cmplxAttrInfo=[AttrInfo(attrName="int_attr",
                                                intAttrType=IntValueType.int)]),
         VariableParams(varName="cmplx_arr", varType="in_out", isComplex=True, isArray=True,
                        isConst=False,
                        cmplxAttrInfo=[AttrInfo(attrName="int_attr",
                                                intAttrType=IntValueType.int)])
         ])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.save_diagram(True)
    def test_node_custom_code(self, super_user, create_catalogs_gen,
                              diagram_constructor, page, allure_step):
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        deploy_page = DeployPage(page=page)
        custom_code_page = CustomCodePage(page=page)
        node_custom_code = CustomCodeConfigurationModal(page=page)
        main_page = MainPage(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        cmplx_type_name = diagram_constructor["var_complex_types"]["cmplx_arr"].objectName
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_catalogs_gen.create_catalog(
                catalog_name=catalog_name)
        with allure_step(f'Создание кастомного кода'):
            with allure_step("Переход во вкладку 'Кастомные коды'"):
                main_page.nav_bar_options(option_name="Разработка").click()
                main_page.development_nav_bar_options(option_name="Кастомные коды").click()
            with allure_step("Выбор каталого и языка для кастомного кода"):
                custom_code_page.add_custom_code.click()
                checkbox_check_action(node_custom_code.modal_window("CustomCodes").
                                      locator(custom_code_page.checkbox_by_row_text(catalog_name)))
                buttons_page.chose_btn.click()
                wait_for_stable(node_custom_code.modal_window("Выбор языка скрипта"))
                custom_code_page.dropdown_by_content("GROOVY").click()
                node_custom_code.option_by_text("PYTHON").last.click()
            with allure_step("Подтверждение первичных настроек"):
                buttons_page.next_btn.click()
        with allure_step("Настройка входных параметров скрипта"):
            with allure_step("Переход во вкладку 'Входные/Выходные данные скрипта'"):
                node_custom_code.option_by_text("Входные/Выходные данные скрипта").click()
            with allure_step("Добавление атрибута и настройка массива комплексной переменной"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(0).fill("array_complex_attr")
                checkbox_check_action(custom_code_page.is_attr_array)
                custom_code_page.attr_type.fill(cmplx_type_name)
                node_custom_code.option_by_text(cmplx_type_name).last.click()
            with allure_step("Добавление атрибута и настройка на числовой тип данных"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(1).fill("int_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Целочисленный (INT)").last.click()
            with allure_step("Добавление атрибута и настройка на числовой тип данных"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(2).fill("long_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Целочисленный (LONG)").last.click()
            with allure_step("Добавление атрибута и настройка на дробный тип данных"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(3).fill("double_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Дробный").last.click()
            with allure_step("Добавление атрибута и настройка на строковый тип данных"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(4).fill("str_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Строковый").last.click()
            with allure_step("Добавление атрибута и настройка на тип данных 'Дата'"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(5).fill("date_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Дата").last.click()
            with allure_step("Добавление атрибута и настройка на логический тип данных"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(6).fill("bool_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Логический").last.click()
            with allure_step("Добавление атрибута и настройка на тип данных 'Время'"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(7).fill("time_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Время").last.click()
            with allure_step("Добавление атрибута и настройка на тип данных 'Дата_время'"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(8).fill("date_time_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Дата_время").last.click()
            with allure_step("Добавление атрибута и настройка массива примитивов"):
                custom_code_page.add_attr("Входные атрибуты").first.click()
                custom_code_page.input_attr_name(9).fill("array_attr")
                checkbox_check_action(custom_code_page.is_attr_array)
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Целочисленный (INT)").last.click()
        with allure_step("Настройка выходных параметров скрипта"):
            with allure_step("Добавление атрибута и настройка на числовой тип данных"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(0).fill("int_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Целочисленный (INT)").last.click()
            with allure_step("Добавление атрибута и настройка на числовой тип данных"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(1).fill("long_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Целочисленный (LONG)").last.click()
            with allure_step("Добавление атрибута и настройка на дробный тип данных"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(2).fill("double_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Дробный").last.click()
            with allure_step("Добавление атрибута и настройка на строковый тип данных"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(3).fill("str_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Строковый").last.click()
            with allure_step("Добавление атрибута и настройка на тип данных 'Дата'"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(4).fill("date_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Дата").last.click()
            with allure_step("Добавление атрибута и настройка на логический тип данных"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(5).fill("bool_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Логический").last.click()
            with allure_step("Добавление атрибута и настройка на тип данных 'Время'"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(6).fill("time_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Время").last.click()
            with allure_step("Добавление атрибута и настройка на тип данных 'Дата_время'"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(7).fill("date_time_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Дата_время").last.click()
            with allure_step("Добавление атрибута и настройка массива примитивов"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(8).fill("array_out_attr")
                custom_code_page.attr_type.click()
                node_custom_code.option_by_text("Целочисленный (INT)").last.click()
                checkbox_check_action(custom_code_page.is_attr_array)
            with allure_step("Добавление атрибута и настройка массива комплексной переменной"):
                custom_code_page.add_attr("Выходные атрибуты").first.click()
                custom_code_page.output_attr_name(9).fill("array_complex_out_attr")
                custom_code_page.attr_type.fill(cmplx_type_name)
                node_custom_code.option_by_text(cmplx_type_name).last.click()
                checkbox_check_action(custom_code_page.is_attr_array)
        with allure_step("Переход в настройки скрипта"):
            node_custom_code.option_by_text("Скрипт").click()
            with allure_step("Ввод скрипта"):
                custom_code_page.textarea.fill("def run(data):\n  return {'int_out_attr': data['int_attr'],\n         "
                                               " 'long_out_attr': data['long_attr'],\n          'double_out_attr': "
                                               "data['double_attr'],\n          'str_out_attr': data['str_attr'],"
                                               "\n          'date_out_attr': data['date_attr'],\n          "
                                               "'bool_out_attr': data['bool_attr'],\n          'time_out_attr': data["
                                               "'time_attr'],\n          'date_time_out_attr': data["
                                               "'date_time_attr'],\n          'array_out_attr': data['array_attr'],"
                                               "\n          'array_complex_out_attr': data['array_complex_attr']} "
                                               )
            with allure_step("Ввод имени скрипта"):
                custom_code_page.script_name.fill(custom_code_name := f"ag_test_python_{generate_string(6)}")
            # with allure_step("Выбор окружения"):
            #     custom_code_page.env_extended_settings.click()
            #     wait_for_stable(node_custom_code.modal_window("Выберите окружение Python"))
            #     checkbox_check_action(custom_code_page.env_checkbox_by_row_text("Python"))
            #     buttons_page.chose_btn.click()
            with allure_step("Сохранение скрипта"):
                custom_code_page.save_script_btn.click()
        with allure_step("Создание пользовательской версии кастомного кода"):
            node_custom_code.option_by_text("Версии").click()
            custom_code_page.user_version_btn.click()
            custom_code_page.user_version_name.fill("user_local")
            buttons_page.save_btn.click()
        with allure_step("Переход на диаграмму"):
            expect(main_page.nav_bar_options(option_name="Разработка")).to_be_visible(timeout=10000)
            main_page.nav_bar_options(option_name="Разработка").click()
            expect(main_page.development_nav_bar_options(option_name="Диаграммы")).to_be_visible(timeout=10000)
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step("Настройка узла 'Кастомный код'"):
            diagram_page.node_on_the_board("кастомный код").click(click_count=2)
            wait_for_stable(node_custom_code.modal_window("кастомный код"))
        with allure_step("Выбор кастомного кода"):
            node_custom_code.custom_code_extended_settings.click()
            node_custom_code.code_search_filed.fill(custom_code_name)
            checkbox_check_action(node_custom_code.input_by_row_text(custom_code_name))
            buttons_page.ok_btn.click()
        with allure_step("Маппинг входных параметров"):
            node_custom_code.checkbox_by_row_text("date_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("date_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("int_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("int_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("str_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("str_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("array_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("int_v_arr", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("time_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("time_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("long_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("long_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("double_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("double_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("bool_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("bool_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("date_time_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("date_time_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("array_complex_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text(cmplx_type_name, "input").last.click()
            buttons_page.add_btn.click()
        with allure_step("Маппинг выходных параметров"):
            node_custom_code.checkbox_by_row_text("date_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("date_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("int_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("int_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("str_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("str_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("array_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("int_v_arr", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("time_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("time_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("long_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("long_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("double_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("double_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("bool_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("bool_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("date_time_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text("date_time_v", "input").last.click()
            buttons_page.add_btn.click()
            node_custom_code.checkbox_by_row_text("array_complex_out_attr", "button").last.click()
            node_custom_code.checkbox_by_row_text(cmplx_type_name, "input").last.click()
            buttons_page.add_btn.click()
        with allure_step("Сохранение узла 'Кастомный код'"):
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
                expect(node_custom_code.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                node_custom_code.button_by_text(text="Далее").click()
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
            wait_for_stable(node_custom_code.modal_window("Параметры развертывания диаграмм"))
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
