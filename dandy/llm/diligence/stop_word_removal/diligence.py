from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Callable

from dandy.llm.diligence.diligence import BaseDiligence

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class StopWordRemovalDiligence(BaseDiligence):
    trigger_level: float = 0.0
    trigger_operator: Callable[[float, float], bool] = operator.le

    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        print('Stop word removal diligence')

