from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from tests.example_project.book.intelligence.plot import bots
from tests.example_project.book.intelligence.plot.intel import PlotPointsIntel

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


def plot_creation(book_intel: BookIntel, chapter_count: int) -> PlotPointsIntel:
    plot_points_intel = bots.PlotOutlineBot().process(
        book_intel=book_intel,
        chapter_count=chapter_count,
    )

    updated_plot_points_intel = PlotPointsIntel()

    for i, plot_point_intel in enumerate(plot_points_intel):
        logging.info(f'Adding a description for plot point {i+1}')
        updated_plot_points_intel.append(
            bots.PlotPointDescriptionBot().process(
                plot_point_intel=plot_point_intel,
                book_intel=book_intel,
                previous_plot_point_intels=updated_plot_points_intel.plot_points,
            )
        )

    return updated_plot_points_intel
