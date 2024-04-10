import time

import allure
import pytest
from playwright.sync_api import expect

from common.generators import generate_string
from products.Decision.e2e.framework.actions import wait_for_stable, checkbox_check_action
from products.Decision.e2e.framework.locators.modal_wndows.communication_channel_modal import CommunicationChannelModal
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.modal_wndows.node_communication import \
    CommunicationChannelConfigurationModal
from products.Decision.e2e.framework.locators.modal_wndows.node_finish import FinishConfigurationModal
from products.Decision.e2e.framework.locators.modal_wndows.versions import SelectVersionModal
from products.Decision.e2e.framework.locators.pages.communication_page import CommunicationPage
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.shared_po.add_new_element_modal import NewElementModal
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.model import DiagramViewDto, ScriptFullView, ScriptVariableFullView, \
    DiagramInOutParameterFullViewDto, ResponseDto
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.framework.steps.decision_steps_script_api import create_groovy_script_user_version
from products.Decision.utilities.custom_code_constructors import code_user_version_construct
from products.Decision.utilities.custom_models import VariableParams, IntValueType
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct


@allure.epic("Канал коммуникации")
@allure.feature("Узел коммуникация")
class TestNodeCommunication:
    @allure.story("Узел канал коммуникации")
    @allure.title('Развёртывание диаграммы с узлом коммуникация с переменной типа int')
    @pytest.mark.nodes(["коммуникация"])
    @pytest.mark.variable_data(
        [VariableParams(varName="date_var", varType="in_out", varDataType=IntValueType.date.value,
                        isConst=False, varValue="date_var"),
         VariableParams(varName="time_var", varType="in_out", varDataType=IntValueType.time.value,
                        isConst=False, varValue="time_var"),
         VariableParams(varName="date_time_var", varType="in_out", varDataType=IntValueType.dateTime.value,
                        isConst=False, varValue="date_time_var"),
         VariableParams(varName="bool_var", varType="in_out", varDataType=IntValueType.bool.value,
                        isConst=False, varValue="bool_var")
         ])
    @pytest.mark.save_diagram(True)
    def test_node_communication(self, super_user, create_dict_gen,
                                diagram_constructor, custom_code_communication, create_code_gen, create_catalogs_gen,
                                faker, page, allure_step):
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        node_name = 'коммуникация'
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        new_element_modal = NewElementModal(page=page)
        versions_modal = SelectVersionModal(page=page)
        deploy_page = DeployPage(page=page)
        communication_channel_page = CommunicationPage(page=page)
        communication_channel_modal = CommunicationChannelModal(page=page)
        node_communication_channel = CommunicationChannelConfigurationModal(page=page)
        node_finish = FinishConfigurationModal(page=page)
        main_page = MainPage(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        script_view: ScriptFullView = custom_code_communication["code_view"]
        script_name = custom_code_communication["script_name"]
        script_text = custom_code_communication["script_text"]
        script_inp_date_time_var: ScriptVariableFullView = custom_code_communication["inp_date_time_var"]
        script_inp_time_var: ScriptVariableFullView = custom_code_communication["inp_time_var"]
        script_inp_str_restrict_var: ScriptVariableFullView = custom_code_communication["inp_str_restrict_var"]
        script_inp_long_var_us_input: ScriptVariableFullView = custom_code_communication["inp_long_var_us_input"]
        script_inp_str_dict_var: ScriptVariableFullView = custom_code_communication["inp_str_dict_var"]
        script_inp_bool_var: ScriptVariableFullView = custom_code_communication["inp_bool_var"]
        script_inp_date_var: ScriptVariableFullView = custom_code_communication["inp_date_var"]
        script_inp_double_restrict_var: ScriptVariableFullView = custom_code_communication["inp_double_restrict_var"]
        script_inp_int_dict_var: ScriptVariableFullView = custom_code_communication["inp_int_dict_var"]
        script_out_date_var: ScriptVariableFullView = custom_code_communication["out_date_var"]
        script_out_bool_var: ScriptVariableFullView = custom_code_communication["out_bool_var"]
        script_out_time_var: ScriptVariableFullView = custom_code_communication["out_time_var"]
        script_out_date_time_var: ScriptVariableFullView = custom_code_communication["out_date_time_var"]
        script_inout_vars = custom_code_communication["inout_var_with_id"]
        script_id = script_view.scriptId
        inout_var_date: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["date_var"]
        inout_time_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["time_var"]
        inout_date_time_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["date_time_var"]
        inout_bool_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["bool_var"]
        with allure_step("Создание пользовательской версии скрипта"):
            script_vers_name = "user_version_" + script_name
            user_body = code_user_version_construct(script_id=script_id,
                                                    script_type="groovy", script_name=script_name,
                                                    script_text=script_text, version_name=script_vers_name,
                                                    variables=script_inout_vars, description=None,
                                                    version_description="different name")
            vers_create_result = ResponseDto.construct(
                **create_groovy_script_user_version(super_user, user_body).body)
        with allure.step("Создание справочников"):
            value_int = dict_value_construct(dict_value="4",
                                             dict_value_display_name="")
            value_int2 = dict_value_construct(dict_value="5",
                                              dict_value_display_name="")
            dict_int_name = "int_test_dict" + generate_string()
            custom_attr_int = dict_construct(
                dict_name=dict_int_name,
                dict_value_type_id="1",
                values=[value_int, value_int2])
            create_dict_gen.create_dict(dict_body=custom_attr_int)
            value_str = dict_value_construct(dict_value="dict_stroka",
                                             dict_value_display_name="")
            value_str2 = dict_value_construct(dict_value="dict_stroka2",
                                              dict_value_display_name="")
            dict_str_name = "str_test_dict" + generate_string()
            custom_attr_str = dict_construct(
                dict_name=dict_str_name,
                dict_value_type_id="2",
                values=[value_str, value_str2])
            create_dict_gen.create_dict(dict_body=custom_attr_str)
        with allure.step("Создание каталога"):
            catalog_name = "ag_test_catalog_" + generate_string()
            create_catalogs_gen.create_catalog(
                catalog_name=catalog_name)
        with allure_step(f'Создание канала коммуникации'):
            with allure_step("Переход во вкладку 'Каналы коммуникации'"):
                main_page.nav_bar_options(option_name="Разработка").click()
                main_page.development_nav_bar_options(option_name="Каналы коммуникации").click()
            with allure_step("Выбор каталога"):
                communication_channel_page.add_communication_channel.click()
                checkbox_check_action(node_communication_channel.modal_window("CommunicationChannels").
                                      locator(communication_channel_page.checkbox_by_row_text(catalog_name)))
                buttons_page.chose_btn.click()
            with allure_step("Ввод имени канала коммуникации"):
                comm_channel_name = f"ag_test_channel_{generate_string(6)}"
                communication_channel_modal.communication_channel_name().fill(comm_channel_name)
            with allure_step("Выбор кастомного кода"):
                communication_channel_modal.custom_code_settings(field_name='Кастомный код').click()
                communication_channel_modal.custom_code_search.fill(script_view.objectName)
                checkbox_check_action(communication_channel_modal.select_custom_code(custom_code_name=script_view.objectName))
                buttons_page.ok_btn.click()
            with allure_step("Выбор версии кастомного кода"):
                communication_channel_modal.custom_code_settings(field_name='Версия скрипта').click()
                versions_modal.search_version.fill(script_vers_name)
                checkbox_check_action(versions_modal.version_checkbox_by_row_text(version_name=script_vers_name))
                buttons_page.chose_btn.click()

            with allure_step("Задание типа ввода значения - ручной ввод"):
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Ввод значения',
                                                                                          var_name=script_inp_long_var_us_input.variableName).click()
                communication_channel_modal.communication_input_settings(input_type='USER_INPUT').check()
                communication_channel_modal.save_input_settings_btn.click()
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Ввод значения',
                                                                                          var_name=script_inp_double_restrict_var.variableName).click()
                communication_channel_modal.communication_input_settings(input_type='USER_INPUT').check()
                communication_channel_modal.communication_setting_restrictions(restriction='Минимальное значение'
                                                                               ).fill("5.5")
                communication_channel_modal.communication_setting_restrictions(restriction='Максимальное значение'
                                                                               ).fill("10.5")
                communication_channel_modal.save_input_settings_btn.click()
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Ввод значения',
                                                                                          var_name=script_inp_str_restrict_var.variableName
                                                                                          ).click()
                communication_channel_modal.communication_input_settings(input_type='USER_INPUT').check()
                communication_channel_modal.communication_setting_restrictions(restriction='Максимальная длина'
                                                                               ).fill("6")
                communication_channel_modal.save_input_settings_btn.click()
            with allure_step("Задание типа ввода значения - справочник"):
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Ввод значения',
                                                                                          var_name=script_inp_int_dict_var.variableName
                                                                                          ).click()
                communication_channel_modal.communication_input_settings(input_type='DICTIONARY').check()
                communication_channel_modal.dictionary_fields(field_name='Справочник').fill(dict_int_name)
                communication_channel_modal.element_from_dropdown(text=dict_int_name).click()
                communication_channel_modal.dictionary_input_method(input_method='Выпадающий список').click()
                communication_channel_modal.element_from_dropdown(text='Радиокнопка').click()
                communication_channel_modal.save_input_settings_btn.click()
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Ввод значения',
                                                                                          var_name=script_inp_str_dict_var.variableName
                                                                                          ).click()
                communication_channel_modal.communication_input_settings(input_type='DICTIONARY').check()
                communication_channel_modal.dictionary_fields(field_name='Справочник').fill(dict_str_name)
                communication_channel_modal.element_from_dropdown(text=dict_str_name).click()
                communication_channel_modal.save_input_settings_btn.click()

            with allure_step("Задание имен атрибутам"):
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_date_time_var.variableName
                                                                                          ).fill(
                    script_inp_date_time_var.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_time_var.variableName
                                                                                          ).fill(
                    script_inp_time_var.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_str_restrict_var.variableName
                                                                                          ).fill(
                    script_inp_str_restrict_var.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_long_var_us_input.variableName
                                                                                          ).fill(
                    script_inp_long_var_us_input.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_str_dict_var.variableName
                                                                                          ).fill(
                    script_inp_str_dict_var.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_bool_var.variableName
                                                                                          ).fill(
                    script_inp_bool_var.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_date_var.variableName
                                                                                          ).fill(
                    script_inp_date_var.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_double_restrict_var.variableName
                                                                                          ).fill(
                    script_inp_double_restrict_var.variableName)
                communication_channel_modal.communication_attr_by_var_name_and_field_name(column_name='Название поля',
                                                                                          var_name=script_inp_int_dict_var.variableName
                                                                                          ).fill(
                    script_inp_int_dict_var.variableName)

            with allure_step("Сохранение канала коммуникации"):
                communication_channel_modal.save_communication_channel_btn.click()
            with allure_step("Создание пользовательской версии канала коммуникации"):
                main_page.search_input.fill(comm_channel_name)
                main_page.communication(communication_name=comm_channel_name).click(click_count=2)
                with allure_step("Переход на вкладку 'Версии'"):
                    communication_channel_modal.switch_to_tab("Версии").click()
                    buttons_page.version_tool_bar(button_name="сохранить").click()
                    comm_vers_name = generate_string(6)
                    communication_channel_modal.user_version_name_and_description(vers_name="Имя версии").fill(
                        comm_vers_name)
                    communication_channel_modal.user_version_name_and_description(vers_description="Описание").fill(
                        generate_string(6))
                    buttons_page.save_btn.click()
                    buttons_page.save_btn.click()
        with allure_step("Переход на диаграмму"):
            expect(main_page.nav_bar_options(option_name="Разработка")).to_be_visible(timeout=10000)
            main_page.nav_bar_options(option_name="Разработка").click()
            expect(main_page.development_nav_bar_options(option_name="Диаграммы")).to_be_visible(timeout=10000)
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step("Настройка узла 'Канал коммуникации'"):
            diagram_page.node_on_the_board("коммуникация").click(click_count=2)
            wait_for_stable(node_communication_channel.modal_window("коммуникация"))
            with allure_step("Выбор канала коммуникации"):
                node_communication_channel.communication_channel_settings(node_name=node_name, field_name='Канал').click()
                node_communication_channel.communication_channel_search.fill(comm_channel_name)
                checkbox_check_action(node_communication_channel.select_communication_channel(communication_channel_name=comm_channel_name))
                buttons_page.ok_btn.click()
            with allure_step("Перевыбор версии канала коммуникации"):
                node_communication_channel.communication_channel_settings(node_name=node_name, field_name='Версия').click()
                versions_modal.search_version.fill(comm_vers_name)
                checkbox_check_action(versions_modal.version_checkbox_by_row_text(version_name=comm_vers_name))
                buttons_page.chose_btn.click()
            with allure_step("Маппинг входных параметров"):
                with allure_step("Маппинг входных переменных на вкладке 'Основные настройки'"):
                    node_communication_channel.user_input(param_name=script_inp_double_restrict_var.variableName).fill(
                        "7.5")
                    node_communication_channel.user_input(param_name=script_inp_str_restrict_var.variableName,
                                                          restriction="Максимальная длина").fill("stroka")
                    node_communication_channel.user_input(param_name=script_inp_long_var_us_input.variableName).fill(
                        "10")
                    node_communication_channel.user_input(param_name=script_inp_str_dict_var.variableName).click()
                    node_communication_channel.element_from_dropdown_with_quotes(text=value_str.dictValue).click()
                    node_communication_channel.user_input(param_name=script_inp_int_dict_var.variableName,
                                                          radio_btn_value=value_int.dictValue).click()
                with allure_step("Переход на вкладку 'Переменные коммуникации'"):
                    node_communication_channel.switch_to_tab("Переменные коммуникации").click()
                node_communication_channel.mapping_by_row_text(tab_name='Переменные коммуникации', param_name=script_inp_bool_var.variableName).click()
                node_communication_channel.checkbox_by_row_text(var_name=inout_bool_var.parameterName).last.click()
                buttons_page.add_btn.click()
                node_communication_channel.mapping_by_row_text(tab_name='Переменные коммуникации', param_name=script_inp_date_time_var.variableName).click()
                node_communication_channel.checkbox_by_row_text(var_name=inout_date_time_var.parameterName).last.click()
                buttons_page.add_btn.click()
                node_communication_channel.mapping_by_row_text(tab_name='Переменные коммуникации', param_name=script_inp_date_var.variableName).click()
                node_communication_channel.checkbox_by_row_text(var_name=inout_var_date.parameterName).last.click()
                buttons_page.add_btn.click()
                node_communication_channel.mapping_by_row_text(tab_name='Переменные коммуникации', param_name=script_inp_time_var.variableName).click()
                node_communication_channel.checkbox_by_row_text(var_name=inout_time_var.parameterName).last.click()
                buttons_page.add_btn.click()
                with allure_step("Маппинг выходных параметров"):
                    with allure_step("Переход на вкладку 'Выходные переменные'"):
                        node_communication_channel.switch_to_tab("Выходные переменные").click()
                    node_communication_channel.mapping_by_row_text(tab_name='Выходные переменные',
                        param_name=script_out_date_time_var.variableName).last.click()
                    node_communication_channel.checkbox_by_row_text(var_name=inout_date_time_var.parameterName).last.click()
                    buttons_page.add_btn.click()
                    node_communication_channel.mapping_by_row_text(tab_name='Выходные переменные', param_name=script_out_bool_var.variableName).last.click()
                    node_communication_channel.checkbox_by_row_text(var_name=inout_bool_var.parameterName).last.click()
                    buttons_page.add_btn.click()
                    node_communication_channel.mapping_by_row_text(tab_name='Выходные переменные', param_name=script_out_time_var.variableName).last.click()
                    node_communication_channel.checkbox_by_row_text(var_name=inout_time_var.parameterName).last.click()
                    buttons_page.add_btn.click()
                    node_communication_channel.mapping_by_row_text(tab_name='Выходные переменные', param_name=script_out_date_var.variableName).last.click()
                    node_communication_channel.checkbox_by_row_text(var_name=inout_var_date.parameterName).last.click()
                    buttons_page.add_btn.click()
            with allure_step("Добавление новой переменной на вкладке 'Переменные коммуникации'"):
                with allure_step("Переход на вкладку 'Переменные коммуникации'"):
                    node_communication_channel.switch_to_tab("Переменные коммуникации").click()
                new_element_modal.button_by_modal_name_number("Переменные коммуникации", number=1).click()
                node_communication_channel.row_field(node_name=node_name, column_name='Значение').click()
                node_communication_channel.checkbox_by_row_text(var_name=inout_var_date.parameterName).last.click()
                buttons_page.add_btn.click()
                node_communication_channel.row_field(node_name=node_name, column_name='Имя').fill(
                    inout_var_date.parameterName + "2")
            with allure_step("Удаление последней созданной переменной"):
                node_communication_channel.row_field(node_name=node_name, column_name='Чекбокс',
                                                     field_value=inout_var_date.parameterName + "2").last.click()
                new_element_modal.button_by_modal_name_number("Переменные коммуникации", number=2).click()
            with allure_step("Добавление еще одной переменной без последующего удаления"):
                new_element_modal.button_by_modal_name_number("Переменные коммуникации", number=1).click()
                node_communication_channel.row_field(node_name=node_name, column_name='Значение').click()
                node_communication_channel.checkbox_by_row_text(var_name=inout_var_date.parameterName).last.click()
                buttons_page.add_btn.click()
                node_communication_channel.row_field(node_name=node_name, column_name='Имя').fill(
                    inout_var_date.parameterName + "3")
        with allure_step('Сохранение узла'):
            new_element_modal.button_by_text(text="Сохранить").click()
            expect(node_communication_channel.loader).to_have_count(1, timeout=5000)
            expect(node_communication_channel.loader).to_have_count(0, timeout=20000)
            expect(node_communication_channel.validation_error).to_have_count(0, timeout=10000)
        # with allure.step('Сохранение узла завершения'):
        #     wait_for_stable(diagram_page.diagram_name_header)
        #     diagram_page.node_on_the_board("Завершение").click(click_count=2)
        #     new_element_modal.button_by_text(text="Сохранить").click()
        #     expect(node_finish.loader).to_have_count(1, timeout=5000)
        #     expect(node_finish.loader).to_have_count(0, timeout=20000)
        #     expect(node_finish.validation_error).to_have_count(0, timeout=10000)
        with allure_step('Сохранение обновлённой диаграммы'):
            with page.expect_response("**/diagrams") as response_info:
                diagram_page.save_btn.click()
            assert response_info.value.status == 201
            wait_for_stable(diagram_page.diagram_name_header)
        with allure_step("Проверка наличия связи канала коммуникации и диаграммы"):
            with allure_step("Переход во вкладку 'Каналы коммуникации'"):
                main_page.nav_bar_options(option_name="Разработка").click()
                main_page.development_nav_bar_options(option_name="Каналы коммуникации").click()
                main_page.search_input.fill(comm_channel_name)
                main_page.communication(communication_name=comm_channel_name).click(click_count=2)
            with allure_step("Переход на вкладку 'Связь с объектами'"):
                communication_channel_modal.switch_to_tab("Связь с объектами").click()
                communication_channel_modal.search_by_row_text(search_text=diagram_data.objectName)
                buttons_page.reject_btn.click()
        with allure_step("Переход в диаграмму"):
            diagram_page.tab_slider_panel(obj_name=diagram_data.objectName).click()
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
                                                   timeout=180000)
