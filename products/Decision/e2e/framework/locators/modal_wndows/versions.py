from typing import Literal

from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class SelectVersionModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)

        self.select_version_modal = page.locator("//*[text()='Выбор версии']/ancestor::div[@class='ant-modal-content']")
        self.search_version = self.select_version_modal.locator("//div[@class='confirm-modal']//*[@placeholder='Поиск...']")

    def version_checkbox_by_row_text(self, version_name: str) -> Locator:
        return self.page.locator(f"//td[text()='{version_name}']//ancestor::tr//input")