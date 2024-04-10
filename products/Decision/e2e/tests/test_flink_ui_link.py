from time import sleep

import allure
import pytest
from playwright.sync_api import expect

from products.Decision.e2e.framework.locators.pages.deploy_page import DeployPage
from products.Decision.e2e.framework.locators.pages.flink_ui_page import FlinkUiPage
from products.Decision.e2e.framework.locators.pages.main_page import MainPage
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status


@allure.epic("Чтение данных")
@allure.feature("Чтение данных")
class TestFlinkUiLink:
    @allure.story("Узел чтения данных")
    @allure.title('Развёртывание диаграммы с узлом чтения, комплексная переменная с атрибутами всех типов')
    @pytest.mark.scenario("DEV-18815")
    def test_flink_ui_link_for_diagram_deployed(self,
                                                super_user,
                                                diagram_deployed, context,
                                                page, allure_step):
        deploy_page = DeployPage(page=page)
        main_page = MainPage(page=page)
        with allure.step("Получение конфигурации развертывания, имени и идентификатора диаграммы и деплоя"):
            diagram_id = diagram_deployed["diagram_id"]
            diagram_name = diagram_deployed["diagram_name"]
            deploy_id = diagram_deployed["deploy_id"]
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure_step('Переход на вкладку администрирование, к списку деплоев'):
            main_page.nav_bar_options(option_name="Администрирование").click()
            main_page.development_nav_bar_options(option_name="Развертывание диаграмм").click()
        with allure_step('Открытие опций развёрнутого деплоя'):
            deploy_page.deploy_options(deploy_id=deploy_id).click()
            expect(deploy_page.flink_ui_button).to_be_enabled(timeout=10000)
        with allure_step('Переход по ссылке на flink ui'):
            with context.expect_page() as flink_page_info:
                deploy_page.flink_ui_button.click()
            flink_page = flink_page_info.value
            flink_page.wait_for_load_state()
            flink_ui_page = FlinkUiPage(page=flink_page)
        with allure_step('У джоба имя диаграммы и статус Running'):
            expect(flink_ui_page.job_name_header).to_contain_text(diagram_name)
            expect(flink_ui_page.job_status).to_contain_text("RUNNING")
        with allure_step('Закрытие страницы флинка'):
            flink_page.close()
        with allure_step('Прожатие чекбокса нужного деплоя'):
            deploy_page.deploy_checkbox_deploy_id(deploy_id=deploy_id).click()
        with allure_step('Остановка выбранного деплоя'):
            deploy_page.stop_deploy_btn.click()
        with allure_step('Обновление списка и состояния деплоев'):
            deploy_page.refresh_deploy_list.click()
        with allure_step('Открытие опций выбранного деплоя'):
            deploy_page.deploy_options(deploy_id=deploy_id).click()
        with allure_step('Кнопка перехода на flink ui недоступна'):
            expect(deploy_page.flink_ui_button).not_to_be_enabled(timeout=10000)
