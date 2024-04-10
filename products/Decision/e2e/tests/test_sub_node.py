from time import sleep

import allure
import pytest

from common.generators import generate_string
from playwright.sync_api import expect
from products.Decision.e2e.framework.actions import *
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.modal_wndows.node_finish import FinishConfigurationModal
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.modal_wndows.node_call import CallConfigurationModal
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.pages.variables_page import VariablesConfigurationModal
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.model import DiagramViewDto
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_nodes import delete_link_by_id
from products.Decision.utilities.custom_models import VariableParams, IntValueType, AttrInfo, IntNodeType


@allure.epic("Поддиаграмма")
@allure.feature("Поддиаграмма")
class TestNodeSub:
    @allure.story("Узел поддиаграмма")
    @allure.title('Развёртывание диаграммы с узлом поддиаграмма, переменные всех примитивных типовб комплексные и '
                  'массивы')
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
         # VariableParams(varName="cmplx_arr", varType="in_out", isComplex=True, isArray=True,
         #                isConst=False,
         #                cmplxAttrInfo=[AttrInfo(attrName="int_attr",
         #                                        intAttrType=IntValueType.int)])
         ])
    @pytest.mark.save_diagram(True)
    def test_node_sub(self, super_user, created_catalog_id,
                      diagram_constructor, faker, save_diagrams_gen, page, allure_step):
        subdiagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        subdiagram_page = DiagramPage(page=page, diagram_uuid=str(subdiagram_data.diagramId))
        deploy_page = DeployPage(page=page)
        call_page = CallConfigurationModal(page=page)
        main_page = MainPage(page=page)
        variable_page = VariablesConfigurationModal(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        cmplx_type_name = diagram_constructor["var_complex_types"]["cmplx"].objectName
        node_finish_modal = FinishConfigurationModal(page=page)
        with allure.step("генерация информации о новой диаграмме"):
            diagram_with_sub_name = "ag_test_with_subdiagram_" + generate_string(16)
            diagram_description = "new diagram created in test"
        with allure.step("Сохранение временной диаграммы, как новой"):
            diagram_with_sub_vers_id = save_diagrams_gen.save_diagram_as_new(
                subdiagram_data.diagramId, subdiagram_data.versionId,
                diagram_with_sub_name, diagram_description
            ).body["uuid"]
        with allure.step("Поиск диаграммы по айди версии"):
            diagram_with_sub_data: DiagramViewDto = DiagramViewDto(**get_diagram_by_version(
                super_user, diagram_with_sub_vers_id
            ).body)
        with allure.step("Удаление связи между узлами"):
            wrong_link_id = list(diagram_with_sub_data.links.keys())[0]
            delete_link_by_id(super_user, wrong_link_id)
            diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_with_sub_data.diagramId))
        with allure_step('Открытие диаграммы'):
            main_page.nav_bar_options(option_name="Разработка").click()
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_with_sub_data.objectName)
            main_page.diagram(diagram_name=diagram_with_sub_data.objectName).click(click_count=2)
        with allure_step('Добавление узла поддиаграммы'):
            wait_for_stable(diagram_page.diagram_name_header)
            diagram_page.get_node(node_type=str(IntNodeType.subdiagram.value)).click(click_count=2)
            buttons_page.zoom_buttons("отдалить").click(click_count=4)
        with allure_step('Привязка узла Фильтр к узлу Исключение'):
            link_nodes(page, from_node=diagram_page.side_by_name_from("Начало"),
                       to_node=diagram_page.side_by_name_to("Поддиаграмма_2"))
            link_nodes(page, from_node=diagram_page.side_by_name_from("Поддиаграмма_2"),
                       to_node=diagram_page.side_by_name_to("Завершение"))
        with allure_step('Открытие узла "Поддиаграмма"'):
            diagram_page.node_on_the_board("Поддиаграмма_2").click(click_count=2)
        with allure_step("Создание новой диаграммы"):
            call_page.create_new_diagramm_btn.click()
            call_page.diagram_search_filed.fill("ag_test_catalog_")
            checkbox_check_action(call_page.checkbox_by_row_text("ag_test_catalog_").first)
            buttons_page.chose_btn.click()
        with allure_step("Ввод имени диаграммы"):
            call_page.option_by_text("Общие данные").click()
            main_page.diagram_name_input.fill(diagram_name := f"ag_test_diagram_{faker.word()}_{faker.pyint()}")
        with allure_step("Ввод переменных диаграммы"):
            call_page.option_by_text("Переменные").click()
            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("int_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(2)).click()
            variable_page.option_by_text("Целочисленный (INT)").click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("int_array_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(4)).last.click()
            variable_page.option_by_text("Целочисленный (INT)").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()
            variable_page.last_row.locator(variable_page.is_array).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("double_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(6).last).click()
            variable_page.option_by_text("Дробный").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("boll_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(8).last).click()
            variable_page.option_by_text("Логический").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("str_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(10).last).click()
            variable_page.option_by_text("Строковый").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("date_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(12).last).click()
            variable_page.option_by_text("Дата").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("date_time_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(14).last).click()
            variable_page.option_by_text("Дата_время").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("time_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(16).last).click()
            variable_page.option_by_text("Время").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("long_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(18).last).click()
            variable_page.option_by_text("Целочисленный (LONG)").last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()

            variable_page.add_new_variable_btn.click()
            variable_page.last_row.locator(variable_page.variable_name_input_field.first).fill("cmplx_attr")
            variable_page.last_row.locator(variable_page.unchecked_in_out_checkboxes.last).click()
            variable_page.last_row.locator(variable_page.dropdown_by_id(20).last).click()
            variable_page.last_row.locator(variable_page.input_by_id(20).last).fill(cmplx_type_name)
            variable_page.option_by_text(cmplx_type_name).last.click()
            variable_page.last_row.locator(variable_page.checked_in_out_checkboxes.first).click()
        with allure_step("Сохранение диаграммы"):
            variable_page.save_diagram_btn.click()
        with allure_step("Создание пользовательской версии диаграммы"):
            call_page.option_by_text("Версии").click()
            variable_page.user_version_btn.click()
            variable_page.user_version_name.fill("user_local")
            buttons_page.save_btn.click()
        with allure_step("Добавление узлов на диаграмму"):
            call_page.option_by_text("Диаграмма").click()
            diagram_page.get_node(node_type="2").click(click_count=2)
            buttons_page.zoom_buttons("отдалить").click(click_count=4)
            diagram_page.get_node(node_type="3").click(click_count=2)
        with allure_step('Привязка узла начала к узлу завершения'):
            link_nodes(page, from_node=diagram_page.side_by_name_from("Начало_0"),
                       to_node=diagram_page.side_by_name_to("Завершение_1"))
        with allure.step('Сохранение узла завершения поддиаграммы'):
            wait_for_stable(diagram_page.diagram_name_header)
            diagram_page.node_on_the_board("Завершение_1").click(click_count=2)
            node_finish_modal.automapping_btn.click()
            with page.expect_response("**/nodes/**") as response_info:
                buttons_page.save_btn.click()
            assert response_info.value.status == 200
        with allure_step("Сохранение диаграммы"):
            diagram_page.save_btn.click()
        with allure_step("Выбор поддиаграммы"):
            with allure_step("Возвращение в основную диаграмму"):
                main_page.nav_bar_options(option_name="Разработка").click()
                main_page.development_nav_bar_options(option_name="Диаграммы").click()
                main_page.search_input.fill(diagram_with_sub_name)
                main_page.diagram(diagram_name=diagram_with_sub_name).last.click(click_count=2)
            with allure_step('Открытие узла "Поддиаграмма"'):
                diagram_page.node_on_the_board("Поддиаграмма_2").click(click_count=2)
            with allure_step("Выбор вызываемой диаграммы"):
                call_page.extended_settings_icon("Название диаграммы").click()
                call_page.diagram_search_filed.fill(diagram_name)
                checkbox_check_action(call_page.service_checkbox(diagram_name))
                buttons_page.ok_btn.click()
            with allure_step("Проверка, что выбралась latest версия поддиаграммы"):
                call_page.dropdown_menu("span", "Версия").click()
                wait_for_stable(call_page.modal_window("Выбор версии"))
                expect(call_page.service_checkbox("LATEST").first).to_be_checked()
                buttons_page.chose_btn.click()
        with allure_step("Маппипнг входных параметров"):
            call_page.extended_settings_by_feature_name("int_attr", "span").first.click()
            call_page.checkbox_by_feature_name("int_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("int_array_attr", "span").first.click()
            call_page.checkbox_by_feature_name("int_v_arr", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("double_attr", "span").first.click()
            call_page.checkbox_by_feature_name("double_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("boll_attr", "span").first.click()
            call_page.checkbox_by_feature_name("bool_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("str_attr", "span").first.click()
            call_page.checkbox_by_feature_name("str_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("date_attr", "span").first.click()
            call_page.checkbox_by_feature_name("date_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("date_time_attr", "span").first.click()
            call_page.checkbox_by_feature_name("date_time_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("time_attr", "span").first.click()
            call_page.checkbox_by_feature_name("time_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("long_attr", "span").first.click()
            call_page.checkbox_by_feature_name("long_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("cmplx_attr", "span").first.click()
            call_page.checkbox_by_feature_name("cmplx", "span").last.click()
            buttons_page.add_btn.click()
        with allure_step("Маппипнг выходных параметров"):
            call_page.extended_settings_by_feature_name("int_attr", "span").last.click()
            call_page.checkbox_by_feature_name("int_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("int_array_attr", "span").last.click()
            call_page.checkbox_by_feature_name("int_v_arr", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("double_attr", "span").last.click()
            call_page.checkbox_by_feature_name("double_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("boll_attr", "span").last.click()
            call_page.checkbox_by_feature_name("bool_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("str_attr", "span").last.click()
            call_page.checkbox_by_feature_name("str_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("date_attr", "span").last.click()
            call_page.checkbox_by_feature_name("date_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("date_time_attr", "span").last.click()
            call_page.checkbox_by_feature_name("date_time_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("time_attr", "span").last.click()
            call_page.checkbox_by_feature_name("time_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("long_attr", "span").last.click()
            call_page.checkbox_by_feature_name("long_v", "span").last.click()
            buttons_page.add_btn.click()

            call_page.extended_settings_by_feature_name("cmplx_attr", "span").last.click()
            call_page.checkbox_by_feature_name("cmplx", "span").last.click()
            buttons_page.add_btn.click()
        with allure_step("Сохранение узла 'Поддиаграмма'"):
            buttons_page.save_btn.click()
        with allure_step('Сохранение узла завершения'):
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
                expect(call_page.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                call_page.button_by_text(text="Далее").click()
            assert response_info.value.status == 201
        with allure_step('Ожидание, что диаграмма успешно отправлена на развёртование'):
            expect(diagram_page.get_success_modal(diagram_name=diagram_with_sub_name)) \
                .to_contain_text(f"Диаграмма {diagram_with_sub_name} была успешно отправлена на развертывание",
                                 timeout=20000)
        with allure_step('Переход на вкладку администрирование, к списку деплоев'):
            main_page.nav_bar_options(option_name="Администрирование").click()
            main_page.development_nav_bar_options(option_name="Развертывание диаграмм").click()
            deploy_id = find_deploy_id(super_user, diagram_with_sub_name, str(diagram_with_sub_data.diagramId))
        with allure_step('Развёртование диаграммы'):
            deploy_page.deploy_checkbox_deploy_id(deploy_id=deploy_id).click()
            deploy_page.deploy_btn.click()
            wait_for_stable(call_page.modal_window("Параметры развертывания диаграмм"))
            deploy_config_modal.diagram_selector.click(force=True)
            deploy_config_modal.element_from_dropdown(text=diagram_with_sub_name).click()
            expect(buttons_page.deploy_btn.last).to_be_enabled(timeout=20000)
            buttons_page.deploy_btn.last.click()
        with allure_step("Идентификация, что диаграмма находится в процессе развертывания"):
            expect(deploy_page.deploy_status_by_deploy_id(deploy_id=deploy_id)).to_have_text("На развертывании",
                                                                                             timeout=20000)
        with allure_step("Идентификация, что развертывание произошло успешно"):
            expect(deploy_page.deploy_status_by_deploy_id(deploy_id=deploy_id),
                   "ожидание деплоя").to_have_text("Развернута",
                                                   timeout=200000)
