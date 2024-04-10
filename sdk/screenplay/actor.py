from typing import Any, Type, TypeVar, Callable
from time import time, sleep

from sdk.user.user import User

from sdk.screenplay.ability import Ability
from sdk.screenplay.action import Action
from sdk.screenplay.question import Question


TypeAbility = TypeVar('TypeAbility', bound=Ability)
T = TypeVar('T')


class Actor(User):
    def __init__(self, abilities):
        super().__init__()
        self._abilities: list[Ability] = abilities

    def who_can(self, ability: TypeAbility):
        return self._abilities.append(ability)

    def uses_ability_to(self, ability: Type[TypeAbility]) -> TypeAbility:
        for a in self._abilities:
            if isinstance(a, ability):
                return a

        raise Exception

    def attempts_to(self, action: Action) -> Any:
        return action.perform_as(self)

    def asks_for(self, question: Question) -> Any:
        return question.answer_by(self)

    # TODO actor expects?
    def performs(self, action: Callable[..., T], until: Callable = None, timeout: int = 10, period: int = 1) -> T:
        if until is None:
            return action(self)

        now = time()

        while time() < now + timeout:
            result = action(self)

            if until(result):
                return result

            sleep(period)

        raise TimeoutError
