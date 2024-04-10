from playwright.sync_api import Page

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class ExpressionEditorModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.text_area = page.locator("//textarea")
        self.add_function_btn = page.get_by_text("Добавить функцию")
        self.add_element_btn = page.get_by_text("Добавить элемент данных")