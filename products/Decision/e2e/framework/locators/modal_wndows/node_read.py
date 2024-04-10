from playwright.sync_api import Page
from playwright.sync_api import Locator
from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class NodeReadPage(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.add_table_btn = page.locator("//*[@class='read-modal-content__data-actions']/button[1]")
        self.check_query = page.get_by_role("button", name="Проверить запрос")
        self.textarea = page.locator("//textarea")
        self.roll_list = page.locator("//*[@aria-label='Развернуть строку']")
        self.add_dataprovider_btn = page.locator("//*[@label='Источник данных']/parent::span//button")
        self.expand_table_columns = page.locator("//button[@aria-label='Развернуть строку']")
        self.confirm_table_btn = page.locator("//button[text()='Ок']")

    def get_checkbox_by_row_name(self, table_name: str) -> Locator:
        return self.row(table_name).locator("//input[@type='checkbox']")
