import httpx

from dandy.core.service.service import BaseService
from dandy.processor.processor import BaseProcessor


class HttpService(BaseService['BaseProcessor']):
    obj: BaseProcessor

    @staticmethod
    def get(url: str):
        return httpx.get(url)
