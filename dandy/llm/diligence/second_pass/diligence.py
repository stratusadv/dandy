from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Callable

from dandy.llm.diligence.diligence import BaseDiligence

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class SecondPassRemovalDiligence(BaseDiligence):
    trigger_level: float = 2.0
    trigger_operator: Callable[[float, float], bool] = operator.ge
    requires_new_llm_request: bool = True

    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        llm_connector.request_body.messages.add_message(
            role='user',
            text='Review our conversation and make sure you answered my request to the best of your ability.'
        )

