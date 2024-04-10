from playwright.sync_api import Page
from playwright.sync_api import Locator


class DiagramPage:
    def __init__(self, diagram_uuid: str, page: Page):
        self.page = page
        self.all_nodes = page.locator("//*[@class='custom-diagram-node']")
        self.board = page.locator(".react-flow__pane")
        self.close_diagram_btn = page.locator(".diagram__actions > button")
        self.diagram_name_header = page.locator("//*[@class='diagram__title']")
        self.diagram_uuid = diagram_uuid
        self.submit_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Отправить на развертывание']")
        self.validate_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Проверить']")
        self.save_btn = page.locator("_react=ButtonWidthTooltip[tooltip='Сохранить']")
        self.sidebar = page.locator("//*[@class='sidebar-diagram']")
        self.side_by_node_name = page.locator("//*[@data-handleid='sourceA']")
        self.variables_window = page.get_by_text("Переменные")
        self.diagram_window = page.get_by_text("Диаграмма", exact=True)
        self.clear_notification_btn = page.get_by_text("Очистить всё")

    def get_node(self, node_type: str) -> Locator:
        return self.page.locator(f"//div[@class='node type-{node_type}']")

    def get_success_modal(self, diagram_name: str) -> Locator:
        return self.page.get_by_text(f"Диаграмма {diagram_name} была успешно отправлена на развертывание")

    def go_to_diagram(self) -> None:
        self.page.goto(f'/development/diagrams/{self.diagram_uuid}/diagram')

    def node_on_the_board(self, node_name: str) -> Locator:
        return self.page.locator(f"//p[contains(text(), '{node_name}')]/parent::div")

    def node_on_the_board_strict(self, node_name: str) -> Locator:
        return self.page.locator(f"//p[text()='{node_name}']/parent::div")

    def side_by_name(self, node_name: str) -> Locator:
        return self.node_on_the_board(f"{node_name}"). \
            locator("//ancestor::div[@class='custom-diagram-node__wrapper']"). \
            locator("//following-sibling::*[@data-handleid='sourceA']")

    def side_by_name_from(self, node_name: str) -> Locator:
        return self.node_on_the_board(f"{node_name}"). \
            locator("//ancestor::div[@class='custom-diagram-node__wrapper']"). \
            locator("//following-sibling::*[@data-handleid='sourceA']")

    def side_by_name_to(self, node_name: str) -> Locator:
        return self.node_on_the_board(f"{node_name}"). \
            locator("//ancestor::div[@class='custom-diagram-node__wrapper']"). \
            locator("//following-sibling::*[@data-handleid='sourceB']")

    def tool_buttons(self, tool_type: str):
        return self.page.locator(f"_react=v[tooltip='{tool_type}']")

    def tab_slider_panel(self, obj_name: str) -> Locator:
        return self.page.locator(f"//div[@class='tab-slider-panel']//descendant::span [text()='{obj_name}']")
