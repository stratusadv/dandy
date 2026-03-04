from __future__ import annotations
from dandy.llm.diligence.stop_word_removal.constants import STOP_WORDS
import re

import operator
from typing import TYPE_CHECKING, Callable

from dandy.llm.diligence.diligence import BaseDiligence

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class StopWordRemovalDiligence(BaseDiligence):
    trigger_level: float = 0.2
    trigger_operator: Callable[[float, float], bool] = operator.le
    requires_new_llm_request: bool = False

    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        for i in range(len(llm_connector.request_body.messages)):
            if isinstance(llm_connector.request_body.messages[i], list):
                for k in range(len(llm_connector.request_body.messages[i])):
                    for j in range(len(llm_connector.request_body.messages[i][k].content)):
                        stripped_text = cls.remove_stop_words(llm_connector.request_body.messages[i][k].content[j].text)
                        llm_connector.request_body.messages[i][k].content[j].text = stripped_text
            else:
                for j in range(len(llm_connector.request_body.messages[i].content)):
                    stripped_text = cls.remove_stop_words(llm_connector.request_body.messages[i].content[j].text)
                    llm_connector.request_body.messages[i].content[j].text = stripped_text

        llm_connector.request_body.messages.add_message(
            role='system',
            text='Assume Stop Words',
            prepend=True,
        )

    @staticmethod
    def remove_stop_words(text: str) -> str:
        stop_words = [re.escape(word) for word in STOP_WORDS]
        pattern = r'\b(' + '|'.join(stop_words) + r')\b'

        cleaned_text = re.sub(pattern, '', text.lower())

        return re.sub(r'\s+', ' ', cleaned_text).strip()
