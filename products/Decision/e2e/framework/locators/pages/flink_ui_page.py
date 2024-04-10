from typing import Literal

from playwright.sync_api import Page
from playwright.sync_api import Locator


class FlinkUiPage:
    def __init__(self, page: Page):
        self.page = page
        self.overview_tab = page.locator("li").filter(has_text="Overview")
        self.runng_jobs_tab = page.locator("nz-sider").get_by_text("Running Jobs")
        self.job_status = page.locator("//td[text()=' Job State ']/parent::tr//flink-job-badge//span")
        self.job_name_header = page.locator("//div[@class='ant-descriptions-title ng-star-inserted']")

    def running_job_options(self, job_name,
                            option: Literal["job_name", "start_time", "duration", "end_time", "tasks", "status"]):
        index = 0
        if option == "job_name":
            index = 1
        if option == "start_time":
            index = 2
        if option == "duration":
            index = 3
        if option == "end_time":
            index = 4
        if option == "tasks":
            index = 5
        if option == "status":
            index = 6
        locator = f"//td[text()='{job_name}']/parent::tr/td[{index}]"
        if index == 6:
            locator += "//span"
        return self.page.locator(locator)

    # def job_name_header(self, job_name):
    #     return self.page.get_by_text(f"{job_name}")
