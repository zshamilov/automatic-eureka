from typing import Protocol

from .request import ApiRequest
from .response import ApiResponse


class ApiClient(Protocol):
    def make_request(self, request: ApiRequest, timeout: int = None) -> ApiResponse:
        ...
