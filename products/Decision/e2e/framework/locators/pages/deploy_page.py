from playwright.sync_api import Page
from playwright.sync_api import Locator


class DeployPage:
    def __init__(self, page: Page):
        self.page = page
        self.diagram_name_header = page.locator("//*[@class='page-header__title']")
        self.deploy_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Развертывание']")
        self.stop_deploy_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Отменить развертывание']")
        self.refresh_deploy_list = page.locator("_react=ButtonWidthTooltip[tooltip='Обновить']")
        self.start_deploy = page.get_by_role("button", name="развернуть", exact=True)
        self.flink_ui_button = page.locator("//*[@title='Перейти на Flink UI']")

    def get_success_modal(self, diagram_name: str) -> Locator:
        return self.page.get_by_text(f"Диаграмма {diagram_name} успешно задеплоена")

    def go_to_deploy_list(self) -> None:
        self.page.goto(f'/administration/deploy-diagram')

    def deploy_checkbox_deploy_id(self, deploy_id):
        return self.page.locator(f"//tr[@data-row-key='{deploy_id}']/child::td[1]")

    def deploy_checkbox_by_name(self, diagram_name):
        return self.page.get_by_role("row",
                                     name=f"{diagram_name}").get_by_label("")

    def deploy_options(self, deploy_id):
        return self.page.locator(f"//tr[@data-row-key='{deploy_id}']/td[9]/button")

    def deploy_status_by_name(self, diagram_name):
        return self.page.get_by_role("row",
                                     name=f"{diagram_name}").locator("//*[@class='ant-badge-status-text']")

    def deploy_status_by_deploy_id(self, deploy_id):
        return self.page.locator(f"//tr[@data-row-key='{deploy_id}']//td[6]//span[@class='ant-badge-status-text']")

