from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.service.service import BaseService

if TYPE_CHECKING:
    from dandy.processor.processor import BaseProcessor


class LlmService(BaseService['BaseProcessor']):
    obj: BaseProcessor

    def hello(self):
        return f"Hello, world! {self.obj.__class__.__name__}"
