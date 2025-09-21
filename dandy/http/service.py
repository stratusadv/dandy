from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.http.mixin import HttpServiceMixin


class HttpService(BaseService['HttpServiceMixin']):
    obj: HttpServiceMixin

    @staticmethod
    def get(url: str):
        return httpx.get(url)
