from typing import Literal

from playwright.sync_api import Page


class Buttons:
    def __init__(self, page: Page):
        self.page = page
        self.add_btn = page.get_by_role("button", name="Добавить")
        self.check_btn = page.get_by_role("button", name="Проверить")
        self.chose_btn = page.get_by_role("button", name="Выбрать")
        self.close_btn = page.get_by_role("button", name="Закрыть")
        self.deploy_btn = page.get_by_role("button", name="развернуть")
        self.ok_btn = page.get_by_role("button", name="Ок")
        self.next_btn = page.get_by_role("button", name="Далее")
        self.no_btn = page.get_by_role("button", name="нет", exact=True)
        self.reject_btn = page.get_by_role("button", name="Отмена")
        self.save_btn = page.get_by_role("button", name="Сохранить").last
        self.zoom_less_btn = page.locator("_react=m[title='Отдалить']")

    def zoom_buttons(self, name: Literal["отдалить", "приблизить"]):
        button_index = 0
        if name == "отдалить":
            button_index = 1
        if name == "приблизить":
            button_index = 2
        return self.page.locator(f"//*[@class='custom-diagram-controls__group'][2]/button[{button_index}]")

    def version_tool_bar(self, button_name: Literal["удалить", "обновить", "сделать актуальной", "сохранить", "открыть"]):
        button_index = 0
        if button_name == "удалить":
            button_index = 1
        elif button_name == "обновить":
            button_index = 2
        elif button_name == "сделать актуальной":
            button_index = 3
        elif button_name == "сохранить":
            button_index = 4
        elif button_name == "открыть":
            button_index = 5
        return self.page.locator(f"//div[@role='dialog']//button[@class='toolbar__actions-button button_icon'][{button_index}]")
