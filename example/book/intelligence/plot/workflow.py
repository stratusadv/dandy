from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.workflow import BaseWorkflow

from example.book.intelligence.plot.bots.plot_outline_llm_bot import PlotOutlineLlmBot

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel
    from example.book.intelligence.plot.intel import PlotIntel

class PlotWorkflow(BaseWorkflow):
    @classmethod
    def process(cls, book_intel: BookIntel) -> PlotIntel:
        pass