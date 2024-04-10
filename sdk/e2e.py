import os
import tempfile
from uuid import uuid4
import shutil
import allure
import pytest
import hashlib
from faker import Faker
from contextlib import contextmanager
from playwright.sync_api import StorageState, Page
from typing import Any, Callable, Dict, Generator, List, Optional
from slugify import slugify
from config import settings

from minio import Minio
from minio.error import S3Error
import os
from pathlib import Path


def _build_artifact_test_folder(
    pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str
) -> str:
    output_dir = pytestconfig.getoption("--output")
    return os.path.join(
        output_dir,
        truncate_file_name(slugify(request.node.nodeid)),
        truncate_file_name(folder_or_file_name),
    )


def truncate_file_name(file_name: str) -> str:
    if len(file_name) < 256:
        return file_name
    return f"{file_name[:100]}-{hashlib.sha256(file_name.encode()).hexdigest()[:7]}-{file_name[-100:]}"


@pytest.fixture(scope="function", autouse=True)
def attach_allure_trace(
    request,
    pytestconfig: Any,
):
    yield
    # Check if the test has failed
    if request.node.rep_call.failed:

        output_dir = pytestconfig.getoption("--output")
        sut = pytestconfig.getoption("--sut")

        trace_path = _build_artifact_test_folder(pytestconfig, request, "trace.zip")
        folder = truncate_file_name(slugify(request.node.nodeid))
        file_tag = f"{uuid4()}"
        r = upload_log(trace_path, f"{file_tag}/{folder}", "trace.zip", sut)
        print(r)
        link = f"https://storage-dev.k8s.datasapience.ru/qa-static/{sut}/{file_tag}/{folder}/trace.zip"
        trace_link = f"""
        <a href="https://trace.playwright.dev/?trace={link}" target="_blank">Watch trace</a>
        """
        allure.attach(
            trace_link, name="trace", attachment_type=allure.attachment_type.HTML
        )
        allure.dynamic.description_html(trace_link)
        allure.dynamic.link(link, name="trace", link_type="trace")


def upload_log(file: str, targetfolder: str, filename: str, sut):
    print(settings["MINIO_ACCOUNT"])
    client = Minio(
        "storage-dev.k8s.datasapience.ru",
        access_key=settings["MINIO_ACCOUNT"],
        secret_key=settings["MINIO_KEY"],
    )
    SUT = sut

    try:
        r = client.fput_object(
            f"qa-static",
            f"/{SUT}/{targetfolder}/{filename}",
            file,
            content_type="application/zip",
        )
        return r
    except:
        print("Uploading failed")


@pytest.fixture
def allure_step(page):
    @contextmanager
    def allure_step_context(title):
        with allure.step(title) as step:
            try:
                yield step
            finally:
                screenshot = page.screenshot(full_page=True)
                allure.attach(
                    screenshot,
                    name="screenshot.png",
                    attachment_type=allure.attachment_type.PNG,
                )

    return allure_step_context
