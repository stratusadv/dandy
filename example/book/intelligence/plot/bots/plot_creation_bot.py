from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot

from example.book.intelligence.plot import bots


if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel
    from example.book.intelligence.plot.intel import PlotIntel


class PlotCreationBot(Bot):
    def process(
            self,
            book_intel: BookIntel
    ) -> PlotIntel:
        plot_intel = bots.PlotOutlineBot().process(
            book_intel=book_intel,
        )

        for i, plot_point_intel in enumerate(plot_intel):
            plot_intel[i] = bots.PlotPointDescriptionBot().process(
                plot_point_intel=plot_point_intel,
                book_intel=book_intel,
                previous_plot_point_intels=plot_intel[:i],
            )

        return plot_intel
