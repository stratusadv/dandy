from __future__ import annotations

from typing import TYPE_CHECKING, List

from dandy import Bot, Prompt, cache_to_sqlite
from tests.example_project.book.intelligence.plot.intel import (
    PlotPointIntel,
    PlotPointsIntel,
)
from tests.example_project.book.intelligence.plot.prompts import plot_intel_prompt
from tests.example_project.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


class PlotPointDescriptionBot(Bot):
    role = 'Plot Point Description Writer'
    task = 'Read all the information and write the required plot points.'
    guidelines = Prompt().list(
        [
            'Leave the plot point outline unchanged.',
            'You will create a description for this current plot point.',
        ]
    )

    def process(
        self,
        plot_point_intel: PlotPointIntel,
        book_intel: BookIntel,
        previous_plot_point_intels: List[PlotPointIntel],
    ) -> PlotPointIntel:
        plot_point_prompt = Prompt()

        plot_point_prompt.prompt(book_intel_prompt(book_intel))

        if previous_plot_point_intels:
            plot_point_prompt.prompt(
                plot_intel_prompt(PlotPointsIntel(items=previous_plot_point_intels)),
            )

            plot_point_prompt.line_break()

        plot_point_prompt.text(label='Current Plot Point Outline to write', text=plot_point_intel.outline)

        return self.llm.prompt_to_intel(
            prompt=plot_point_prompt,
            intel_object=plot_point_intel,
            include_fields={'description'},
        )
