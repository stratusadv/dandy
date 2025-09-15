from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.workflow import BaseWorkflow

from example.book.intelligence.plot import bots


if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel
    from example.book.intelligence.plot.intel import PlotIntel


class PlotWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            book_intel: BookIntel
    ) -> PlotIntel:
        plot_intel = bots.PlotOutlineLlmBot.process(
            book_intel=book_intel,
        )

        for i, plot_point_intel in enumerate(plot_intel):
            plot_intel[i] = bots.PlotPointDescriptionLlmBot.process(
                plot_point_intel=plot_point_intel,
                book_intel=book_intel,
                previous_plot_point_intels=plot_intel[:i],
            )

        return plot_intel
