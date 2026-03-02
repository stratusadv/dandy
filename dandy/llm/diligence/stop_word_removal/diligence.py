from __future__ import annotations

import operator
from typing import TYPE_CHECKING

from dandy.llm.diligence.diligence import BaseDiligence

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class StopWordRemovalDiligence(BaseDiligence):
    trigger_level = 0.0
    trigger_operator = operator.le

    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        print('Stop word removal diligence')

