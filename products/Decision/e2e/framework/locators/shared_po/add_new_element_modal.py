from typing import Literal

from playwright.sync_api import Page

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class NewElementModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.new_el_modal_add_btn = page.locator("//div[@class='modal__box add-element__table']//button")

    def field(self, name: Literal["Наименование элемента", "Массив", "Тип элемента", "Выбрать из списка флаг",
                                  "Выбрать из списка", "Относится к объекту", "Используется только внутри диаграммы"]):
        index = 0
        if name == "Наименование элемента":
            index = 1
        if name == "Массив":
            index = 2
        if name == "Тип элемента":
            index = 3
        if name == "Выбрать из списка флаг":
            index = 4
        if name == "Выбрать из списка":
            index = 5
        if name == "Относится к объекту":
            index = 6
        if name == "Используется только внутри диаграммы":
            index = 7
        return self.page.locator(f"//tr[@data-row-key='0']//td[{index}][contains(@class, 'ant-table-cell')]//input")

    def add_el_modal_btn(self, button_name: str):
        return self.page.locator(f"//div[@class='add-new-element']//button[text()='{button_name}']")

    def selector_arrow_from_field(self, name: Literal["Наименование элемента", "Массив", "Тип элемента", "Выбрать из списка флаг",
                                  "Выбрать из списка", "Относится к объекту", "Используется только внутри диаграммы"]):
        index = 0
        if name == "Наименование элемента":
            index = 1
        if name == "Массив":
            index = 2
        if name == "Тип элемента":
            index = 3
        if name == "Выбрать из списка флаг":
            index = 4
        if name == "Выбрать из списка":
            index = 5
        if name == "Относится к объекту":
            index = 6
        if name == "Используется только внутри диаграммы":
            index = 7
        return self.page.locator(f"//tr[@data-row-key='0']//td[{index}][contains(@class, 'ant-table-cell')]//span["
                                 f"@class='ant-select-arrow']")
