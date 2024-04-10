from typing import Literal

from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class CommunicationChannelConfigurationModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)

        self.communication_channel_select_modal = page.locator(
            "//*[text()='CommunicationChannels']/ancestor::div[@class='ant-modal-content']")
        self.communication_channel_search = self.communication_channel_select_modal.locator(
            "//div[@class='ant-modal-body']//*[@placeholder='Поиск...']")
        self.new_element_mapping = page.locator("//tr[descendant::input[@type='checkbox'][not(@disabled)]]//button")
        self.new_element_checkbox = page.locator("//input[@type='checkbox'][not(@disabled)]")

    def communication_node_modal(self, node_name: str) -> Locator:
        return self.page.locator(f"//*[text()='{node_name}']/ancestor::div[@class='ant-modal-content']")

    def communication_channel_settings(self, node_name: str, field_name: Literal['Канал', 'Версия']) -> Locator:
        return self.communication_node_modal(node_name=node_name).locator(
            f"//span[input[@label='{field_name}']]//button[starts-with(@class, '_inputButton')]")

    def select_communication_channel(self, communication_channel_name: str) -> Locator:
        return self.communication_channel_select_modal.locator(
            f"//span[text()='{communication_channel_name}']//ancestor::tr//input")

    def communication_node_tab(self, tab_name: str) -> Locator:
        return self.page.locator(f"//span[text()='{tab_name}']//ancestor::div[@class='modal__box']")

    def checkbox_by_row_text(self, var_name: str) -> Locator:
        return self.page.locator(f"//tr[descendant::*[text()='{var_name}']]//input")

    def mapping_by_row_text(self, tab_name: Literal['Переменные коммуникации', 'Выходные переменные'],
                            param_name: str) -> Locator:
        return self.communication_node_tab(tab_name=tab_name).locator(
            f"//tr[descendant::input[@value='{param_name}']]//button")

    def user_input(self, param_name: str, restriction=None, radio_btn_value=None) -> Locator:
        if restriction == "Максимальная длина":
            return self.communication_node_tab(tab_name='Основные настройки').locator(
                f"//*[text()='{param_name}']//parent::div//textarea")
        elif radio_btn_value:
            return self.communication_node_tab(tab_name='Основные настройки').locator(
                f"//div[@class='ant-radio-group ant-radio-group-outline']//span[text()='{radio_btn_value}']")
        elif restriction is None and radio_btn_value is None:
            return self.communication_node_tab(tab_name='Основные настройки').locator(
                f"//*[text()='{param_name}']//parent::div//input")

    def row_field(self, node_name: str, column_name: Literal['Чекбокс', 'Имя', 'Тип', 'Значение'],
                  field_value: str = "") -> Locator:
        index = 0
        input_type = ''
        if column_name == 'Чекбокс':
            index = 1
            input_type = 'input'
        elif column_name == 'Имя':
            index = 2
            input_type = 'input'
        elif column_name == 'Тип':
            index = 3
            input_type = 'input'
        elif column_name == 'Значение':
            index = 4
            input_type = 'button'
        locator = self.communication_node_modal(node_name=node_name).locator(
            f"//input[@value='{field_value}' and @type!='checkbox']//ancestor::tr/td[{index}]//{input_type}")
        return locator
