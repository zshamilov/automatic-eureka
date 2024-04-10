from typing import Literal

from playwright.sync_api import Page, Locator

from products.Decision.e2e.framework.locators.shared_po.modal_window_common import ModalWindowConfiguration


class DeployConfigModal(ModalWindowConfiguration):
    def __init__(self, page: Page):
        ModalWindowConfiguration.__init__(self, page=page)
        self.apply_for_selector = page.locator("//div[@class='deploy-settings-top-group-left']//input")
        self.diagram_selector = page.locator("//div[@class='deploy-settings-top-group-right']/div[1]//input")
        self.subdiagram_selector = page.locator("//div[@class='deploy-settings-top-group-right']/div[2]//input")