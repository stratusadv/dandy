from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from dandy.llm.diligence.diligence import BaseDiligence
from dandy.llm.diligence.second_pass.diligence import SecondPassRemovalDiligence
from dandy.llm.diligence.stop_word_removal.diligence import StopWordRemovalDiligence

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector

class BaseDiligenceHandler(ABC):
    diligence_classes: tuple[type[BaseDiligence]]

    def __init__(self, level: float) -> None:
        self.level = level


    def apply(self, llm_connector: LlmConnector) -> None:
        for diligence_class in self.diligence_classes:
            if diligence_class.is_triggered(self.level):
                diligence_class.apply(llm_connector=llm_connector)

class PreDiligenceHandler(BaseDiligenceHandler):
    diligence_classes = (
        StopWordRemovalDiligence,
    )


class PostDiligenceHandler(BaseDiligenceHandler):
    diligence_classes = (
        SecondPassRemovalDiligence,
    )


