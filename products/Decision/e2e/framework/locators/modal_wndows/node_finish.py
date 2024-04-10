from typing import Literal

from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class FinishConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.automapping_btn = page.locator("//*[text()='Выходные атрибуты']/ancestor::div"
                                            "[@class='modal__box-header']/div[@class='modal__box-toolbar']/button[1]")

    def finish_var(self, var_name: str, field: Literal["Атрибут", "Тип", "Значение",
                                                       "Аварийное значение", "Null значение"],
                   element: str = "input") -> Locator:
        index = 0
        if field == "Атрибут":
            index = 1
        if field == "Тип":
            index = 2
        if field == "Значение":
            index = 3
        if field == "Аварийное значение":
            index = 4
        if field == "Null значение":
            index = 5
        return self.page.locator(f"//*[text()='{var_name}']/ancestor::tr//td[{index}]//{element}")