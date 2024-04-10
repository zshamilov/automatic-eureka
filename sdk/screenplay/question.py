from typing import Protocol, Any


class Question(Protocol):
    def answer_by(self, actor: 'Actor') -> Any:
        ...
