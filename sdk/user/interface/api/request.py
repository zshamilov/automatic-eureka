from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ApiRequest:
    method: str
    path: str
    headers: dict
    query: dict
    body: dict
    files: list = None


