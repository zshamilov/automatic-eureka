from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class CustomCodeConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)

        self.custom_code_extended_settings = page.locator("//button[starts-with(@class, '_inputButton')][not("
                                                          "@disabled)]")
        self.code_search_filed = page.locator("//*[text()='CustomCodes']/ancestor::div["
                                              "@class='ant-modal-content']//*[@placeholder='Поиск...']")

    def input_by_row_text(self, content: str) -> Locator:
        return self.page.locator(f"//span[text()='{content}']//ancestor::tr//input")

    def checkbox_by_row_text(self, feature_name: str, checkbox_type: str, descendant: str = "*") -> Locator:
        return self.page.locator(f"//tr[descendant::{descendant}[text()='{feature_name}']]//{checkbox_type}")
