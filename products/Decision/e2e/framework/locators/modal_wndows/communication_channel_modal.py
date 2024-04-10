from typing import Literal

from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class CommunicationChannelModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)

        self.parameter_input_settings_modal = page.locator("//*[text()='Настройка ввода параметра']/ancestor::div[@class='ant-modal-content']")
        self.attr_name = page.locator(
            "//td[descendant::input[@value='input_var']]//preceding-sibling::td//child::input")
        self.save_communication_channel_btn = page.locator("//*[text()='Сохранить']")
        self.save_input_settings_btn = page.locator("//*[text()='Настройка ввода параметра']//ancestor::div["
                                                    "@class='ant-modal-header']//following::div["
                                                    "@class='ant-modal-footer']//*[text()='Сохранить']")
        self.custom_code_select_modal = page.locator(
            "//*[text()='CustomCodes']/ancestor::div[@class='ant-modal-content']")
        self.custom_code_search = self.custom_code_select_modal.locator(
            "//div[@class='ant-modal-body']//*[@placeholder='Поиск...']")

    def communication_modal(self, modal_type: Literal[
        'Новый канал коммуникации', 'Редактирование канала коммуникации'] = 'Новый канал коммуникации') -> Locator:
        return self.page.locator(f"//*[text()='{modal_type}']/ancestor::div[@class='ant-modal-content']")

    def communication_channel_name(self, modal_type: Literal[
        'Новый канал коммуникации', 'Редактирование канала коммуникации'] = 'Новый канал коммуникации') -> Locator:
        return self.communication_modal(modal_type=modal_type).locator("//input[@label='Название канала']")

    def custom_code_settings(self, field_name: Literal['Кастомный код', 'Версия скрипта'], modal_type: Literal[
        'Новый канал коммуникации', 'Редактирование канала коммуникации'] = 'Новый канал коммуникации') -> Locator:
        return self.communication_modal(modal_type=modal_type).locator(
            f"//span[input[@label='{field_name}']]//button[starts-with(@class, '_inputButton')]")

    def select_custom_code(self, custom_code_name: str) -> Locator:
        return self.custom_code_select_modal.locator(f"//span[text()='{custom_code_name}']//ancestor::tr//input")

    def communication_attr_by_var_name_and_field_name(self,
                                                      column_name: Literal[
                                                          'Название поля', 'Атрибут', 'Массив', 'Тип', 'Ввод значения'],
                                                      var_name: str) -> Locator:
        field_index = 0
        input_type = ''
        if column_name == 'Название поля':
            field_index = 1
            input_type = "input"
        elif column_name == 'Атрибут':
            field_index = 2
            input_type = "input"
        elif column_name == 'Массив':
            field_index = 3
        elif column_name == 'Тип':
            field_index = 4
        elif column_name == 'Ввод значения':
            field_index = 5
            input_type = "button"

        return self.communication_modal().locator(
            f"//input[@value='{var_name}']//ancestor::tr//td[{field_index}]//{input_type}")

    def communication_input_settings(self,
                                     input_type: Literal['DIAGRAM_ELEMENT', 'USER_INPUT', 'DICTIONARY']) -> Locator:
        return self.parameter_input_settings_modal.locator(f"//span[@class='ant-radio']//input[@value = '{input_type}']")

    def communication_setting_restrictions(self, restriction: Literal[
        'Минимальное значение', 'Максимальное значение', 'Максимальная длина']) -> Locator:
        return self.parameter_input_settings_modal.locator(f"//*[text()='{restriction}']//following-sibling::div[1]//input")

    def dictionary_fields(self, field_name: Literal['Справочник', 'Способ ввода']) -> Locator:
        return self.parameter_input_settings_modal.locator(f"//*[text()='{field_name}']//following::input[1]")

    def dictionary_input_method(self, input_method: Literal['Выпадающий список', 'Радиокнопка']):
        return self.parameter_input_settings_modal.locator(f"//span[text()='{input_method}']")

    def search_by_row_text(self, search_text: str, modal_type: Literal[
        'Новый канал коммуникации', 'Редактирование канала коммуникации'] = 'Новый канал коммуникации') -> Locator:
        return self.communication_modal(modal_type=modal_type).locator(f"//td[text()='{search_text}']//ancestor::tr")