from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.application.diligence.diligence import BaseDiligence

if TYPE_CHECKING:
    from dandy.infrastructure.llm.connector import LlmConnector


class SecondPassRemovalDiligence(BaseDiligence):
    requires_new_llm_request: bool = True

    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        llm_connector.request_body.messages.add_message(
            role='user',
            text=(
                'Review our conversation and make sure you answered my request '
                'to the best of your ability.'
            ),
        )
