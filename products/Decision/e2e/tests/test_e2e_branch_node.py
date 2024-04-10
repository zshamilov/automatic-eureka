from time import sleep

import allure
import pytest
from playwright.sync_api import expect

from products.Decision.e2e.framework.actions import wait_for_stable
from products.Decision.e2e.framework.locators.modal_wndows.deploy_config import DeployConfigModal
from products.Decision.e2e.framework.locators.modal_wndows.node_branch import BranchConfigurationModal
from products.Decision.e2e.framework.locators.modal_wndows.node_finish import FinishConfigurationModal
from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.diagram_page import DiagramPage
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.e2e.framework.locators.shared_po.buttons import Buttons
from products.Decision.framework.model import DiagramViewDto
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id
from products.Decision.utilities.custom_models import VariableParams, IntValueType, NodeFullInfo, IntNodeType

@allure.epic("Ветвление")
@allure.feature("Ветвление")
class TestNodeJdbcWrite:
    @allure.story("Узел ветвления")
    @allure.title('Развёртывание диаграммы с узлом ветвления, 2 ветви по значению')
    @pytest.mark.variable_data([VariableParams(varName="out_int", varType="out", varDataType=IntValueType.int.value),
                                VariableParams(varName="in_str", varType="in", varDataType=IntValueType.str.value)])
    @pytest.mark.node_full_info([NodeFullInfo(nodeType=IntNodeType.branch, nodeName="Ветвление",
                                              linksFrom=["Начало"],
                                              # linksTo=["Завершение", "Завершение_1"],
                                              coordinates=(800, 202)),
                                 NodeFullInfo(nodeType=IntNodeType.finish, nodeName="Завершение_1",
                                              coordinates=(1800, 402))])
    @pytest.mark.save_diagram(True)
    def test_node_branch(self, super_user,
                         diagram_constructor, faker, page, allure_step):
        diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        diagram_page = DiagramPage(page=page, diagram_uuid=str(diagram_data.diagramId))
        deploy_page = DeployPage(page=page)
        branch_modal = BranchConfigurationModal(page=page)
        finish_modal = FinishConfigurationModal(page=page)
        main_page = MainPage(page=page)
        buttons_page = Buttons(page=page)
        deploy_config_modal = DeployConfigModal(page=page)
        with allure_step(f'Открытие диаграммы'):
            main_page.nav_bar_options(option_name="Разработка").click()
            main_page.development_nav_bar_options(option_name="Диаграммы").click()
            main_page.search_input.fill(diagram_data.objectName)
            main_page.diagram(diagram_name=diagram_data.objectName).click(click_count=2)
        with allure_step('Открытие узла ветвления для его настройки'):
            wait_for_stable(diagram_page.diagram_name_header)
            buttons_page.zoom_buttons("отдалить").click(click_count=4)
            diagram_page.node_on_the_board(node_name="Ветвление").click(click_count=2)
        with allure_step('Выбор элемента по которому производится ветвление'):
            branch_modal.element_name_btn.click()
            expect(branch_modal.value_checkbox_by_row_key(name="in_str")).to_be_enabled()
            branch_modal.value_checkbox_by_row_key(name="in_str").check()
            branch_modal.button_by_text('Добавить').click()
        with allure_step('Проверка, что подсказка содержит нужный текст'):
            branch_modal.hint_icon.click()
            branch_modal.hint_text.focus()
            branch_modal.hint_text.click()
            expect(branch_modal.hint_text).\
                to_have_text("Строковое значение должно быть обернуто в кавычки ' '.")
            wait_for_stable(branch_modal.modal_window(modal_window_name="Ветвление"))
        with allure_step('Добавление первой ветки'):
            branch_modal.branches_buttons(btn_type="добавить ветвь").click()
            with allure_step('Заполнение значения ветвления'):
                branch_modal.branches_table(brunch_num=1, field="Значение").fill("'string1'")
            with allure_step('Указание целевого узла: первый узел завершения'):
                branch_modal.branches_table(brunch_num=1, field="Целевой узел").click()
                expect(branch_modal.target_node_checkbox(node_name="Завершение")).to_be_visible()
                branch_modal.target_node_checkbox(node_name="Завершение").click()
                buttons_page.ok_btn.click()
        with allure_step('Заполнение ветки иначе: второй узел завершения'):
            branch_modal.else_branch_target_node_btn.click()
            expect(branch_modal.target_node_checkbox(node_name="Завершение_1")).to_be_visible()
            branch_modal.target_node_checkbox(node_name="Завершение_1").click()
            buttons_page.ok_btn.click()
        with allure_step('Сохранение узла'):
            with page.expect_response("**/nodes/**") as response_info:
                branch_modal.button_by_text(text="Сохранить").click()
            assert response_info.value.status == 200
        with allure_step('Открытие узла Завершение_1 для его настройки'):
            diagram_page.node_on_the_board(node_name="Завершение_1").click(click_count=2)
            finish_modal.finish_var(var_name="out_int", field="Значение").fill("0")
        with allure_step('Сохранение узла Завершение_1'):
            with page.expect_response("**/nodes/**") as response_info:
                branch_modal.button_by_text(text="Сохранить").click()
            assert response_info.value.status == 200
            wait_for_stable(diagram_page.diagram_name_header)
        with allure_step('Открытие узла Завершение для его настройки'):
            expect(diagram_page.node_on_the_board_strict(node_name="Завершение")).to_be_visible(timeout=20000)
            diagram_page.node_on_the_board_strict(node_name="Завершение").click(click_count=2)
            finish_modal.finish_var(var_name="out_int", field="Значение").fill("1")
        with allure_step('Сохранение узла Завершение'):
            with page.expect_response("**/nodes/**") as response_info:
                branch_modal.button_by_text(text="Сохранить").click()
            assert response_info.value.status == 200
            wait_for_stable(diagram_page.diagram_name_header)
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
                expect(branch_modal.button_by_text(text="Далее")).to_be_visible(timeout=20000)
                branch_modal.button_by_text(text="Далее").click()
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
            wait_for_stable(branch_modal.modal_window("Параметры развертывания диаграмм"))
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
