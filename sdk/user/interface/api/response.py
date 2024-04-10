from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import requests


@dataclass
class ApiResponse:
    status: int
    reason: str
    body: dict
    headers: dict
    elapsed: timedelta
    content: Optional[bytes]
    raw: requests.Response
