from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class InsertConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.confirm_button = page.get_by_role("button", name="Ок", exact=True)
        self.insert_type_dropdown = page.locator("//*[@class='ant-select-selector']")
        self.provider_select_btn = page.locator("//input[@label='Источник данных']/parent::span//button")
        self.table_select_button = page.locator("//input[@label='Таблица']/parent::span//button")
        self.search_table_field = page.get_by_placeholder("Поиск...")
        self.confirm_table_btn = page.locator("//button[text()='Ок']")

    def insert_type(self, insert_type: str) -> Locator:
        return self.page.get_by_text(insert_type)

    def null_value_checkbox(self, content: str) -> Locator:
        return self.page.locator(f"//tr[.//*[text()='{content}']]").locator(self.element_by_type("checkbox"))

    def select_table(self, source_id: str, table_name: str) -> Locator:
        return self.page.locator(f"//tr[@data-row-key='{source_id}_{table_name}_public']/child::td[1]//span[@class='ant-checkbox']")

    def select_value_checkbox(self, value: str) -> Locator:
        return self.page.locator(f"//tr[@data-row-key='{value}']//span[@class='ant-checkbox']")

    def get_checkbox_by_row_name(self, table_name: str) -> Locator:
        return self.row(table_name).locator("//input[@type='checkbox']")




