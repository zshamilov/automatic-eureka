from typing import Protocol, ContextManager
from typing import Any, Optional


class Reporter(Protocol):
    @staticmethod
    def attach(title: str, text: str, data: Optional[Any]) -> None:
        ...

    @staticmethod
    def step(text: str) -> ContextManager:
        ...
