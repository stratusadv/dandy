from dataclasses import dataclass
from typing import Optional, Union

from dandy.core.url import Url


@dataclass(kw_only=True)
class ServiceSettings:
    url: Url
    port: int
    model: str
    headers: dict
    retry_count: int = 10
