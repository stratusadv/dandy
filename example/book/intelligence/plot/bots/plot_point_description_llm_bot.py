from __future__ import annotations

from typing_extensions import TYPE_CHECKING, List

from dandy.cache import cache_to_sqlite
from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.plot.intel import PlotPointIntel, PlotIntel
from example.book.intelligence.plot.prompts import plot_intel_prompt
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class PlotPointDescriptionLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text("You are a plot point description bot.")
        .text(
            "You will be given information on the book and will use the following rules:"
        )
        .list(
            [
                "Leave the plot point outline unchanged.",
                "You will create a description for this current plot point.",
            ]
        )
    )

    @classmethod
    @cache_to_sqlite('example')
    def process(
            cls,
            plot_point_intel: PlotPointIntel,
            book_intel: BookIntel,
            previous_plot_point_intels: List[PlotPointIntel],
    ) -> PlotPointIntel:
        prompt = Prompt()

        prompt.prompt(book_intel_prompt(book_intel))

        if previous_plot_point_intels:
            prompt.prompt(plot_intel_prompt(
                PlotIntel(items=previous_plot_point_intels)),
            )

            prompt.line_break()

        prompt.text(label='Current Plot Point Outline', text=plot_point_intel.outline)

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_object=plot_point_intel,
            include_fields={'description'},
        )
