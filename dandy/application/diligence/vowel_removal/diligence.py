from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.application.diligence.diligence import BaseDiligence
from dandy.application.diligence.vowel_removal.constants import VOWELS

if TYPE_CHECKING:
    from dandy.infrastructure.llm.connector import LlmConnector


class VowelRemovalDiligence(BaseDiligence):
    @classmethod
    def apply(cls, llm_connector: LlmConnector) -> None:
        for i in range(len(llm_connector.request_body.messages)):
            if isinstance(llm_connector.request_body.messages[i], list):
                for k in range(len(llm_connector.request_body.messages[i])):
                    for j in range(len(llm_connector.request_body.messages[i][k].content)):
                        stripped_text = cls.remove_vowels(
                            llm_connector.request_body.messages[i][k].content[j].text
                        )
                        llm_connector.request_body.messages[i][k].content[j].text = stripped_text
            else:
                for j in range(len(llm_connector.request_body.messages[i].content)):
                    stripped_text = cls.remove_vowels(
                        llm_connector.request_body.messages[i].content[j].text
                    )
                    llm_connector.request_body.messages[i].content[j].text = stripped_text

        cls._prepend_system_instruction(llm_connector, 'Assume Vowels')

    @staticmethod
    def remove_vowels(text: str) -> str:
        remove_str = ''.join(VOWELS)

        translation_table = str.maketrans('', '', remove_str)

        return text.lower().translate(translation_table)
