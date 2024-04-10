import os
import allure
import pytest
from faker import Faker
from contextlib import contextmanager
from playwright.sync_api import StorageState, Page
from typing import Any, Callable, Dict, Generator, List, Optional

from common.generators import generate_string
from products.Decision.framework.model import VariableType1, ScriptFullView, ScriptVariableFullView
from products.Decision.framework.steps.decision_steps_deploy import (
    deploy_list_by_status,
)
from products.Decision.framework.steps.decision_steps_diagram import stop_deploy
from products.Decision.framework.steps.decision_steps_script_api import create_groovy_script, get_groovy_script_by_id
from products.Decision.utilities.custom_code_constructors import script_vars_construct, code_construct
from sdk.e2e import attach_allure_trace, allure_step


@pytest.fixture(scope="class")
def credentials_(super_user) -> dict:
    return {
        "username": super_user.username,
        "password": super_user.password,
    }


@pytest.fixture(scope="class")
def storage_state(browser, base_url, credentials_) -> StorageState:
    with browser.new_context() as context:
        with context.new_page() as page:
            context.set_default_timeout(10000)
            page.goto(base_url)
            page.wait_for_selector("[name=username]").fill(credentials_["username"])
            page.wait_for_selector("[name=password]").fill(credentials_["password"])
            page.wait_for_selector("[name=login]").click()
            return context.storage_state()


@pytest.fixture(scope="class")
def browser_context_args(base_url, storage_state) -> dict:
    return {
        "base_url": base_url,
        "storage_state": storage_state,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture(autouse=True)
def decision_is_opened(page) -> None:
    page.goto("/")


@pytest.fixture(scope="class")
def faker():
    return Faker(["en-US"]).unique


@pytest.fixture(scope="function", autouse=True)
def deploy_clean_up(request, super_user) -> None:
    def stop_running_deploys():
        deploy_list = deploy_list_by_status(super_user, deploy_status="DEPLOYED")
        for deploy in deploy_list:
            deploy_id = deploy["deployId"]
            stop_deploy(super_user, deploy["deployId"])

    request.addfinalizer(stop_running_deploys)
