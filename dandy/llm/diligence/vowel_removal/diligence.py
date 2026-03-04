from __future__ import annotations
from dandy.llm.diligence.vowel_removal.constants import VOWELS
from dandy.llm.diligence.stop_word_removal.constants import STOP_WORDS
import re

import operator
from typing import TYPE_CHECKING, Callable

from dandy.llm.diligence.diligence import BaseDiligence

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class VowelRemovalDiligence(BaseDiligence):
    trigger_level: float = 0.0
    trigger_operator: Callable[[float, float], bool] = operator.le

    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        for i in range(len(llm_connector.request_body.messages)):
            if isinstance(llm_connector.request_body.messages[i], list):
                for k in range(len(llm_connector.request_body.messages[i])):
                    for j in range(len(llm_connector.request_body.messages[i][k].content)):
                        stripped_text = cls.remove_vowels(llm_connector.request_body.messages[i][k].content[j].text)
                        llm_connector.request_body.messages[i][k].content[j].text = stripped_text
            else:
                for j in range(len(llm_connector.request_body.messages[i].content)):
                    stripped_text = cls.remove_vowels(llm_connector.request_body.messages[i].content[j].text)
                    llm_connector.request_body.messages[i].content[j].text = stripped_text

        llm_connector.request_body.messages.add_message(
            role='system',
            text='Assume Vowels',
            prepend=True,
        )

    @staticmethod
    def remove_vowels(text: str) -> str:
        remove_str = ''.join(VOWELS)

        translation_table = str.maketrans('', '', remove_str)

        return text.lower().translate(translation_table)
