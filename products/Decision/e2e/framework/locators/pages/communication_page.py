from typing import Literal

from playwright.sync_api import Page, expect
from playwright.sync_api import Locator
from playwright.sync_api import Page


class CommunicationPage:
    def __init__(self, page: Page):
        self.page = page
        self.add_communication_channel = page.locator("_react=ButtonWidthTooltip[tooltip='Добавить']")

    def checkbox_by_row_text(self, content: str) -> Locator:
        return self.page.locator(f"//td[*[text()='{content}']]//preceding-sibling::td//input")
