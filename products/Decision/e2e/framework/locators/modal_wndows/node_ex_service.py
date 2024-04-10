from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class ExServiceConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.service_search_filed = page.locator("//*[text()='ExternalServices']/ancestor::div["
                                                 "@class='ant-modal-content']//*[@placeholder='Поиск...']")

    def extended_settings_icon(self, header: str) -> Locator:
        return self.page.locator(f"//*[contains(.//span, '{header}')]/following-sibling::span//button")

    def service_checkbox(self, content: str) -> Locator:
        return self.get_row_by_its_content(content).locator(self.input_by_value(""))
