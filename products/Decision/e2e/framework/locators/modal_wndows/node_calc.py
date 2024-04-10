from typing import Literal

from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class CalcConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)

    def vars_table(self, var_name, field: Literal["Чекбокс", "Имя переменной", "Тип", "Относится к объекту",
                                                  "Значение"], element: str = "input") -> Locator:
        cell_index = 0
        if field == "Чекбокс":
            cell_index = 1
        if field == "Имя переменной":
            cell_index = 2
        if field == "Тип":
            cell_index = 3
        if field == "Относится к объекту":
            cell_index = 4
        if field == "Значение":
            cell_index = 5
        return self.page.locator(f"//*[@value='{var_name}']/ancestor::tr//td[{cell_index}]//{element}")