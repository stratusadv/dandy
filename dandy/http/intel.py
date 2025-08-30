from dandy.intel.intel import BaseIntel


class HttpResponseIntel(BaseIntel):
    _httpx_response: dict
    status_code: int