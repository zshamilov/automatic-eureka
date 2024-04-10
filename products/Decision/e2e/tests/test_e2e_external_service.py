import time
import allure
import pytest

from playwright.sync_api import expect
from products.Decision.e2e.framework.actions import *
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.modal_wndows.node_ex_service import ExServiceConfigurationModal
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.model import DiagramViewDto
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Вызов Внешнего Сервиса")
@allure.feature("Вызов Внешнего Сервиса")
class TestNodeExService:
    @allure.story("Узел внешний сервис")
    @allure.title('Развёртывание диаграммы с узлом внешний сервис')
    @allure.issue("DEV-14329")
    @pytest.mark.environment_dependent
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
    @pytest.mark.nodes(["внешний сервис"])
    @pytest.mark.save_diagram(True)
    def test_node_ex_service(self, super_user,
                             diagram_constructor, faker, page, allure_step):
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        deploy_page = DeployPage(page=page)
        main_page = MainPage(page=page)
        ex_service_page = ExServiceConfigurationModal(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        with allure_step('Открытие диаграммы'):
            main_page.nav_bar_options(option_name="Разработка").click()
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step('Открытие узла "Внешний сервис"'):
            diagram_page.node_on_the_board("внешний сервис").click(click_count=2)
            wait_for_stable(ex_service_page.modal_window("внешний сервис"))
            with allure_step("Выбор сервиса"):
                ex_service_page.dropdown_menu("span", "Имя сервиса").click()
                ex_service_page.service_search_filed.fill("LV_for_e2e")
                checkbox_check_action(ex_service_page.service_checkbox("LV_for_e2e"))
                buttons_page.ok_btn.click()
            with allure_step("Проверка, что выбралась latest версия сервиса"):
                ex_service_page.dropdown_menu("span", "Версия").click()
                wait_for_stable(ex_service_page.modal_window("Выбор версии"))
                expect(ex_service_page.service_checkbox("LATEST")).to_be_checked(timeout=10000)
            with allure_step("Выбор другой версии"):
                checkbox_check_action(ex_service_page.service_checkbox("user_local"))
                buttons_page.chose_btn.click()
        with allure_step("Маппинг входных параметров"):
            ex_service_page.input_button_by_content("in").click()
            with allure_step("Проверка, что доступны для выбора только для строкового типа данных"):
                expect(ex_service_page.checkbox_by_feature_name("long_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("double_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("bool_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("int_v", "span")).to_be_disabled()
            with allure_step("Выбор элемента данных"):
                checkbox_check_action(ex_service_page.checkbox_by_feature_name("str_v", "span"))
                buttons_page.add_btn.click()
        with allure_step("Маппинг выходных параметров"):
            with allure_step("Маппинг логической переменной"):
                ex_service_page.input_button_by_content("isCat_var").click()
            with allure_step("Проверка, что доступны для выбора только элементы соответствующего типа"):
                expect(ex_service_page.checkbox_by_feature_name("long_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("double_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("int_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("str_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
            with allure_step("Выбор элемента данных"):
                checkbox_check_action(ex_service_page.checkbox_by_feature_name("bool_v", "span"))
                buttons_page.add_btn.click()
            with allure_step("Маппинг дробной переменной"):
                ex_service_page.input_button_by_content("weight_var").click()
            with allure_step("Проверка, что доступны для выбора только элементы соответствующего типа"):
                expect(ex_service_page.checkbox_by_feature_name("long_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("bool_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("int_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("str_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
            with allure_step("Выбор элемента данных"):
                checkbox_check_action(ex_service_page.checkbox_by_feature_name("double_v", "span"))
                buttons_page.add_btn.click()
            with allure_step("Маппинг переменной типа 'Дата'"):
                ex_service_page.input_button_by_content("birthday_var").click()
            with allure_step("Проверка, что доступны для выбора только элементы соответствующего типа"):
                expect(ex_service_page.checkbox_by_feature_name("long_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("double_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("bool_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("int_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("str_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("time_v", "span")).to_be_disabled()
            with allure_step("Выбор элемента данных"):
                checkbox_check_action(ex_service_page.checkbox_by_feature_name("date_v", "span"))
                buttons_page.add_btn.click()
            with allure_step("Маппинг целочисленной переменной"):
                ex_service_page.input_button_by_content("age_var").click()
            with allure_step("Проверка, что доступны для выбора только элементы соответствующего типа"):
                expect(ex_service_page.checkbox_by_feature_name("long_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("double_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("bool_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("str_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
            with allure_step("Выбор элемента данных"):
                checkbox_check_action(ex_service_page.checkbox_by_feature_name("int_v", "span"))
                buttons_page.add_btn.click()
            with allure_step("Маппинг строковой переменной"):
                ex_service_page.input_button_by_content("name_var").click()
            with allure_step("Проверка, что доступны для выбора только элементы соответствующего типа"):
                expect(ex_service_page.checkbox_by_feature_name("long_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("double_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("bool_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_time_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("int_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
            with allure_step("Выбор элемента данных"):
                checkbox_check_action(ex_service_page.checkbox_by_feature_name("str_v", "span"))
                buttons_page.add_btn.click()
            with allure_step("Маппинг переменной типа Дата-время"):
                ex_service_page.input_button_by_content("lastVisitToVet_var").click()
            with allure_step("Проверка, что доступны для выбора только элементы соответствующего типа"):
                expect(ex_service_page.checkbox_by_feature_name("long_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("double_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("bool_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("str_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("int_v", "span")).to_be_disabled()
                expect(ex_service_page.checkbox_by_feature_name("date_v", "span")).to_be_disabled()
            with allure_step("Выбор элемента данных"):
                checkbox_check_action(ex_service_page.checkbox_by_feature_name("date_time_v", "span"))
                buttons_page.add_btn.click()
            with allure_step("Сохранение узла 'Внешний сервис'"):
                buttons_page.save_btn.click()
                sleep(10)
        # with allure_step('Открытие узла "Завершение"'):
        #     diagram_page.node_on_the_board("Завершение").click(click_count=2)
        #     wait_for_stable(ex_service_page.modal_window("Завершение"))
        #     with allure_step("Маппинг переменных"):
        #         ex_service_page.input_button_by_content("int_v").click()
        #         ex_service_page.checkbox_by_feature_name("int_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #         ex_service_page.input_button_by_content("double_v").click()
        #         ex_service_page.checkbox_by_feature_name("double_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #         ex_service_page.input_button_by_content("str_v").click()
        #         ex_service_page.checkbox_by_feature_name("str_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #         ex_service_page.input_button_by_content("date_v").click()
        #         ex_service_page.checkbox_by_feature_name("date_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #         ex_service_page.input_button_by_content("bool_v").click()
        #         ex_service_page.checkbox_by_feature_name("bool_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #         ex_service_page.input_button_by_content("date_time_v").click()
        #         ex_service_page.checkbox_by_feature_name("date_time_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #         ex_service_page.input_button_by_content("time_v").click()
        #         ex_service_page.checkbox_by_feature_name("time_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #         ex_service_page.input_button_by_content("long_v").click()
        #         ex_service_page.checkbox_by_feature_name("long_v", "span").last.click()
        #         buttons_page.add_btn.click()
        #     with allure_step("Сохранение настроенного узла"):
        #         buttons_page.save_btn.click()
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
                expect(ex_service_page.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                ex_service_page.button_by_text(text="Далее").click()
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
            wait_for_stable(ex_service_page.modal_window("Параметры развертывания диаграмм"))
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
