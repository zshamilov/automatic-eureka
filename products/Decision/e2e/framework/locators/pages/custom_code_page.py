from playwright.sync_api import Page
from playwright.sync_api import Locator


class CustomCodePage:
    def __init__(self, page: Page):
        self.page = page
        self.add_custom_code = page.locator("_react=ButtonWidthTooltip[tooltip='Добавить']")
        self.attr_name = page.locator("//input[@value='' and @type='text'] and not(@placeholder = 'Поиск...')")
        self.attr_type = page.locator("//input[@type='search']").last
        self.env_extended_settings = page.locator("//button[starts-with(@class, 'input-ext')]")
        self.is_attr_array = page.locator("//input[@type='checkbox'][not(@disabled)]").last
        self.save_script_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Сохранить']")
        self.script_name = page.locator("//input[@label='Название скрипта']")
        self.textarea = page.locator("//textarea")
        self.validate_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Проверить']")
        self.user_version_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Сохранить пользовательскую версию']")
        self.user_version_name = page.locator("//input[@label='Имя версии']")

    def add_attr(self, header: str) -> Locator:
        return self.page.locator(f"//*[contains(.//span, '{header}')]//button[@class='button_icon']")

    def checkbox_by_row_text(self, content: str) -> Locator:
        return self.page.locator(f"//td[*[text()='{content}']]//preceding-sibling::td//input")

    def env_checkbox_by_row_text(self, content: str) -> Locator:
        return self.page.locator(f"//tr[.//*[text()='{content}']]//input")

    def dropdown_by_content(self, content: str) -> Locator:
        return self.page.locator(f"//*[@title='{content}']")

    def input_attr_name(self, number: int):
        return self.page.locator(f"//tr[@data-row-key='input-{number}']//input[@type='text']")

    def output_attr_name(self, number: int):
        return self.page.locator(f"//tr[@data-row-key='output-{number}']//input[@type='text']")
