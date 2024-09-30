from dataclasses import dataclass
from typing_extensions import List, Dict
from urllib.parse import urlencode, urlparse, ParseResult, quote


@dataclass(kw_only=True)
class Url:
    host: str
    path_parameters: List[str] = list
    query_parameters: Dict[str, str] = dict


    @property
    def parsed_url(self) -> ParseResult:
        return urlparse(self.host)

    @property
    def path(self) -> str:
        return self.path_parameters_to_str + self.query_parameters_to_str

    @property
    def is_https(self) -> bool:
        return self.parsed_url.scheme == 'https'

    @property
    def path_parameters_to_str(self) -> str:
        if self.path_parameters:
            return '/' + '/'.join([quote(parameter) for parameter in self.path_parameters])

        return ''

    @property
    def query_parameters_to_str(self) -> str:
        if self.query_parameters:
            query = urlencode(self.query_parameters)
            return '?' + query

        return ''
