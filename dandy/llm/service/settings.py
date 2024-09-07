from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class ServiceSettings:
    url: str
    port: Optional[Union[int, str]] = None
    headers: Optional[dict] = None
    path_parameters: Optional[list] = None
    query_parameters: Optional[dict] = None
    retry_count: int = 10