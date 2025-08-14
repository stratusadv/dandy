from dandy.http.service import HttpService


class HttpProcessorMixin:
    http: HttpService = HttpService()