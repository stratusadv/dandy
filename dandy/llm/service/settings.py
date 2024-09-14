from dataclasses import dataclass
from typing import Optional, Union


@dataclass(kw_only=True)
class ServiceSettings:
    url: str
    model: str
    port: Optional[Union[int, str]] = None
    headers: Optional[dict] = None
    path_parameters: Optional[list] = None
    query_parameters: Optional[dict] = None
    retry_count: int = 10