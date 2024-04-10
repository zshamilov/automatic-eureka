from typing import Protocol


class WebClient(Protocol):
    def __init__(self):
        raise NotImplemented('web client is\'t implemented')
