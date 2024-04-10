from typing import Protocol, Any


class Action(Protocol):
    def perform_as(self, actor: 'Actor') -> Any:
        ...
