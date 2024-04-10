from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class VariablesConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.add_new_variable_btn = page.locator("//span[text()='Внешние параметры диаграммы']/"
                                                 "ancestor::div[@class='ant-collapse-header']"
                                                 "//*[@class='toolbar']//button[1]")
        self.checked_in_out_checkboxes = page.locator("_react=[value='OUT']")
        self.is_array = page.locator("_react=[value=false]").first
        self.last_row = page.locator("//tr").last
        self.save_diagram_btn = page.locator("_react=[title='Сохранить']")
        self.variable_name_input_field = page.locator("//input[@type='text' and @value='']")
        self.unchecked_in_out_checkboxes = page.locator("_react=[value='IN']")
        self.user_version_btn = page.locator("_react=Anonymous[name='icon-version_save']")
        self.user_version_name = page.locator("//input[@label='Имя версии']")

    def dropdown_by_id(self, id: int) -> Locator:
        return self.page.locator(f"//*[@id='rc_select_{id}']/parent::span/following-sibling::span")

    def input_by_id(self, id: int) -> Locator:
        return self.page.locator(f"//*[@id='rc_select_{id}']")

    def reserved_value_by_row_content(self, content: str) -> Locator:
        return self.page.locator(f"//tr[.//*[@value='{content}']]//*[@class='ant-input-suffix']")
