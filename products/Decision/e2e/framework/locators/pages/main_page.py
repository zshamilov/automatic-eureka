from playwright.sync_api import Page
from playwright.sync_api import Locator


class MainPage:
    def __init__(self, page: Page):
        self.page = page
        self.add_new_one_button = page.locator('.toolbar__actions-button').first
        self.diagram_name_input = page.locator("//input[@label='Название диаграммы']")
        self.search_input = page.get_by_placeholder("Поиск")

    def nav_bar_options(self, option_name: str) -> Locator:
        return self.page.get_by_role("menuitem", name=f"{option_name}").locator("path")

    def development_nav_bar_options(self, option_name: str) -> Locator:
        # self.page.get_by_role("link", name=f"{option_name}")
        return self.page.get_by_text(f"{option_name}")

    def diagram(self, diagram_name: str) -> Locator:
        return self.page.get_by_text(f"{diagram_name}", exact=True)

    def communication(self, communication_name: str) -> Locator:
        return self.page.get_by_text(f"{communication_name}", exact=True)
