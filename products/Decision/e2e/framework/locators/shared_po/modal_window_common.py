from playwright.sync_api import Page
from playwright.sync_api import Locator
from typing import Union


class ModalWindowConfiguration:
    def __init__(self, page: Page):
        self.page = page
        self.add_btn = page.locator("_react=v[tooltip='Добавить']")
        self.custom_code_dropdown_last_option = page.locator("div[class^='ant-select']").last
        self.droppable_field = page.locator("//*[@data-rbd-droppable-id='chose']")
        self.remain_switch = page.locator("//button[@role='switch']")
        self.validation_error = page.locator("//div[@role='dialog']//h2[text()='Обнаружены ошибки валидации блока']")
        self.loader = page.locator("//div[@class='ant-modal-content']//div[@class='loader']//span[@role='img']")

    def button_by_cell_value(self, cell_value: str) -> Locator:
        return self.page.locator(f"//input[@value='{cell_value}']//ancestor::td//button")

    def field_by_cell_value(self, cell_value: str) -> Locator:
        return self.page.locator(f"//input[@value='{cell_value}']//ancestor::td//input[@type='text']")

    def button_by_modal_name_and_cell_value(self, modal_name: str, cell_value: str) -> Locator:
        return self.page.locator(f"//*[(@class='modal__box') and contains(.//span, '{modal_name}')]"
                                 f"//input[@value='{cell_value}']//ancestor::td//button")

    def button_by_text(self, text: str) -> Locator:
        return self.page.locator(f"//button[text() = '{text}']")

    def button_by_modal_name_number(self, name: str, number: int) -> Locator:
        return self.page.locator(f"//*[(@class='modal__box-header') and contains(.//span, '{name}')]//button[{number}]")

    def add_button_by_modal_name(self, name: str, field: str = "title"):
        return self.page.locator(f"_react=[{field}='{name}']").locator("_react=[tooltip='Добавить']")

    def checkbox(self) -> Locator:
        return self.page.locator("//*[@type='checkbox']")

    def checkbox_by_feature_name(self, feature_name: str, descendant: str = "div") -> Locator:
        return self.page.locator(f"//tr[descendant::{descendant}[text()='{feature_name}']]//input")

    def diagram_var_content_button(self, var_name: str) -> Locator:
        return self.page.locator(f"//tr[@data-row-key='{var_name}']//button")

    def dropdown_menu(self, following_sibling: str, header: str) -> Locator:
        return self.page.locator(f"//*[contains(.//span, '{header}')]"
                                 f"/following-sibling::{following_sibling}//span")

    def element_by_type(self, type: str) -> Locator:
        return self.page.locator(f"//*[@type='{type}']")

    def element_from_dropdown(self, text: str):
        return self.page.locator(f"//div[@class='ant-select-item-option-content' and text() = '{text}']")

    def element_from_dropdown_with_quotes(self, text: str):
        return self.page.locator(f"//div[@class='ant-select-item-option-content' and text() = \"'{text}'\"]")

    def get_add_delete_buttons(self, row_name: str) -> Locator:
        return self.page.locator(f"//*[text()='{row_name}']/parent::div//button")

    def get_row_by_its_content(self, content: str) -> Locator:
        return self.page.locator(f"//tr[.//*[text()='{content}']]")

    def get_value_field_by_placeholder(self, placeholder: str = "") -> Locator:
        return self.page.locator(f"//*[@placeholder='{placeholder}']")

    def input_by_id(self, id: int) -> Locator:
        return self.page.locator(f"_react=Selector[id='rc_select_{id}']")

    def input_by_value(self, value: str) -> Locator:
        return self.page.locator(f"//*[@value='{value}']")

    def input_button_by_content(self, content: str) -> Locator:
        return self.page.locator(f"//tr[.//*[text()='{content}']]//button")

    def option_by_text(self, option: str) -> Locator:
        return self.page.locator(f"//*[text()='{option}']")

    def modal_window(self, modal_window_name: str) -> Locator:
        return self.page.locator(f"//*[@class='ant-modal-content'][descendant::*[text()='{modal_window_name}']]")

    def row(self, index: Union[int, str]) -> Locator:
        return self.page.locator(f"tr[data-row-key*='{index}']")

    def row_alternative(self, index: int) -> Locator:
        return self.page.locator(f"//tr[@index='{index}']")

    def value_checkbox_by_name(self, name: str) -> Locator:
        loc = self.page.get_by_role("row", name=name).get_by_label("")
        return loc

    def value_checkbox_by_row_key(self, name: str) -> Locator:
        loc = self.page.locator(f"//tr[@data-row-key='{name}']//span")
        return loc.first

    def user_version_name_and_description(self, vers_name=None, vers_description=None) -> Locator:
        if vers_name == "Имя версии":
            return self.page.locator(f"//input[@label='{vers_name}']")
        elif vers_description == "Описание":
            return self.page.locator("//textarea")

    def switch_to_tab(self, tab_name: str) -> Locator:
        return self.page.locator(f"//p[text()='{tab_name}']")

