from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class CallConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.create_new_diagramm_btn = page.locator("//button[text()='Создать новую диаграмму']")
        self.diagram_search_filed = page.locator("//*[text()='Diagrams']/ancestor::div["
                                                 "@class='ant-modal-content']//*[@placeholder='Поиск...']")

    def checkbox_by_row_text(self, content: str) -> Locator:
        return self.page.locator(f"//td[*[contains(text(), '{content}')]]//preceding-sibling::td//input")

    def extended_settings_by_feature_name(self, feature_name: str, descendant: str = "div") -> Locator:
        return self.page.locator(f"//tr[descendant::{descendant}[text()='{feature_name}']]//button")

    def extended_settings_icon(self, header: str) -> Locator:
        return self.page.locator(f"//*[contains(.//span, '{header}')]/following-sibling::span//button")

    def service_checkbox(self, content: str) -> Locator:
        return self.get_row_by_its_content(content).locator(self.input_by_value(""))
