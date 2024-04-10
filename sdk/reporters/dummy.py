import shutil
from contextlib import contextmanager
import os
import sys
import json
from rich import print
from rich import print_json
from rich.pretty import pprint
import glamor as allure
import logging
from rich.logging import RichHandler
from rich.pretty import pretty_repr
from rich.padding import Padding
from rich.panel import Panel
from rich.theme import Theme
from rich.highlighter import RegexHighlighter
from rich.console import Group
from rich.console import Console
from rich.text import Text
from rich.style import Style
from requests.exceptions import RequestException, HTTPError
from sdk.user.interface.api.request import ApiRequest
from sdk.user.interface.api.response import ApiResponse


class RequestHighlighter(RegexHighlighter):
    base_style = "req."
    highlights = [r"^(?P<status>\d+)", r"\s(?P<reason>\w+)\s", r"(?P<stats>(ms|s))$"]


theme = Theme(
    {
        "req.status": Style.parse("bold cyan"),
        "req.reason": Style.parse("magenta"),
        "req.result": Style.parse("yellow"),
        "req.stats": Style.parse("dim"),
    }
)
console = Console(theme=theme, record=True, log_path=False, markup=False)


@contextmanager
def tab(title, width):

    console.print(title)
    yield
    console.print(f" ")


class Dummy:
    MAX_LENGTH = 65536
    OUTPUT_TRUNCATED = f'... output truncated, text exceeds maximum length ({MAX_LENGTH})'

    @staticmethod
    def cut_the_crap(s: str | bytes) -> str:
        return f'{s[:Dummy.MAX_LENGTH]}{Dummy.OUTPUT_TRUNCATED}' if len(s) > Dummy.MAX_LENGTH else f'{s}'

    # NB console.print ужасно медленно работает с большими объемами данных
    @staticmethod
    def attach(title, text, data=None):
        if title in ["ApiResponse", "ApiRequest", "RequestException"]:
            if isinstance(data, ApiResponse):
                console.print(f'Response: {text}')

                crap = json.dumps(data.body, ensure_ascii=False, indent=2) if data.body != {} else data.content
                console.print(Dummy.cut_the_crap(crap))

                if os.getenv("ALLURE") == "True":
                    allure.attach(console.export_text(), f"RESPONSE: {data.status}", allure.attachment_type.TEXT)

            if isinstance(data, ApiRequest):
                headers_dcit = Text()
                for k, v in data.headers.items():
                    if k != "Authorization":
                        headers_dcit.append(f"{k}: {v}\n")

                if data.body:
                    console.print("Body: ")
                    console.print_json(data=data.body)

                if data.query:
                    console.print("params: ")
                    for key, value in data.query.items():
                        console.print(Text(f"{key} = {value}"))

                if data.files:
                    console.print("files: ")
                    console.print(data.files)

                if os.getenv("ALLURE") == "True":
                    s = Dummy.cut_the_crap(console.export_text())
                    allure.attach(s, f"{text}", allure.attachment_type.TEXT)

            if title == "RequestException":
                if isinstance(data, HTTPError):
                    console.print(f"{text}: {data.response.status_code}")
                    console.print(data)

                    try:
                        console.print_json(data=data.response.json())
                    except:
                        console.print(data.response.text)

                    if os.getenv("ALLURE") == "True":
                        s = Dummy.cut_the_crap(console.export_text())
                        allure.attach(s, f"HTTPError: {text}", allure.attachment_type.TEXT)

                else:
                    console.print(data)
                    console.print_exception(show_locals=True)

                    if os.getenv("ALLURE") == "True":
                        s = Dummy.cut_the_crap(console.export_text())
                        allure.attach(s, f"RequestException", allure.attachment_type.TEXT)

        else:
            console.log(title, text)

    @staticmethod
    def step(title):
        return tab(title, shutil.get_terminal_size().columns - 1)
