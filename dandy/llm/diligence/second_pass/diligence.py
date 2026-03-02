from __future__ import annotations

import operator
from typing import TYPE_CHECKING

from dandy.llm.diligence.diligence import BaseDiligence

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class SecondPassRemovalDiligence(BaseDiligence):
    trigger_level = 2.0
    trigger_operator = operator.ge

    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        print('Second pass removal diligence')

