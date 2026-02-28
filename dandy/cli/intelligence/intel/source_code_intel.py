from typing import Literal

from dandy import BaseIntel


class SourceCodeIntel(BaseIntel):
    language: Literal['python']
    extension: Literal['py']
    code: str