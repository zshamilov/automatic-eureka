from typing import Literal

from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class BranchConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.element_name_btn = page.locator("//*[@label='Имя элемента']/parent::span//button")
        self.hint_icon = page.locator("//*[text()='Тип данных']//span")
        self.hint_text = page.locator("//div[@role='tooltip']//span")
        self.else_branch_target_node_btn = page.locator("//*[text()='Иначе']/ancestor::tr//td[3]//button")

    def branches_buttons(self, btn_type: Literal["добавить ветвь", "удалить ветвь"]) -> Locator:
        index = 0
        if btn_type == "добавить ветвь":
            index = 1
        if btn_type == "удалить ветвь":
            index = 2
        return self.page.locator(f"//div[@class='branch-modal-content']//button[@class='button_icon'][{index}]")

    def branches_table(self, brunch_num, field: Literal["Чекбокс", "Оператор", "Значение", "Целевой узел"]) -> Locator:
        element = "input"
        cell_index = 0
        if field == "Чекбокс":
            cell_index = 1
        if field == "Оператор":
            cell_index = 2
        if field == "Значение":
            cell_index = 3
        if field == "Целевой узел":
            element = "button"
            cell_index = 4
        return self.page.locator(f"//tbody//tr[{brunch_num}]//td[{cell_index}]//{element}")

    def target_node_checkbox(self, node_name: str) -> Locator:
        return self.page.locator(f"//td[text()='{node_name}']//ancestor::tr//label")

