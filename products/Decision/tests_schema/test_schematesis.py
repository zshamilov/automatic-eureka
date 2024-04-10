import functools
import os

import glamor as allure
import schemathesis
import pytest
from dotenv import load_dotenv


def call_once(func):
    seen = set()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        test_name = os.environ.get("PYTEST_CURRENT_TEST")
        if test_name in seen:
            return
        seen.add(test_name)
        return func(*args, **kwargs)

    return wrapper


@call_once
def title(value):
    allure.dynamic.title(value)


@call_once
def story(value):
    allure.dynamic.story(value)


# schema = schemathesis.from_uri("https://decision-qa.k8s.datasapience.ru/api/v3/api-docs")
schema = schemathesis.from_uri(os.environ.get("API_SCHEME_URL"))


@schema.parametrize()
def test_api(case, super_user):
    title(case.method)
    story(case.endpoint.path)
    with allure.step(
            f"Endpoint: {case.formatted_path}; Query: {case.query}; Body: {case.body}"
    ):
        resp = case.call(headers={"Authorization": f"Bearer {super_user.with_api.token}"})

        resp_to_attach = f"{resp.request.method}\n{resp.request.url}\n{resp.status_code}\n{resp.text}"

        allure.attach(resp_to_attach, name="output", attachment_type=allure.attachment_type.TEXT)

        case.validate_response(resp)
