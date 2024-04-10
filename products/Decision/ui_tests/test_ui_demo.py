import playwright
from playwright.sync_api import Page, expect
from playwright.sync_api import Playwright, sync_playwright, expect
import pytest


@pytest.fixture()
def page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect("ws://browserless.k8s.datasapience.ru/playwright" )
        #browser = playwright.chromium.connect("ws://localhost:3000/playwright" )
        #browser = playwright.chromium.launch()
        # Create a new context and page
        context = browser.new_context(ignore_https_errors=True, screen={"width": 1980, "height": 1080}, viewport={"width": 1980, "height": 1080})

        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        yield page
        context.tracing.stop(path = "trace.zip")
        context.close()
        browser.close()


def test_example(page) -> None:
    page.goto("https://decision-qa.k8s.datasapience.ru/")
    page.get_by_label("Username or email").click()
    page.get_by_label("Username or email").fill("writer")
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill("writer")
    page.get_by_role("button", name="Sign In").click()
    expect(page.locator(".home__content")).to_be_visible()

