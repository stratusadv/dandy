from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.http.mixin import HttpProcessorMixin


class HttpService(BaseService['HttpProcessorMixin']):
    obj: HttpProcessorMixin

    @staticmethod
    def get(url: str):
        return httpx.get(url)
