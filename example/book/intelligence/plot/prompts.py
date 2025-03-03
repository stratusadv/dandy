from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.llm import Prompt

if TYPE_CHECKING:
    from example.book.intelligence.plot.intel import PlotIntel


def plot_intel_prompt(plot_intel: PlotIntel) -> Prompt:
    prompt = Prompt()
    prompt.text('Plot Points:')

    for i, plot_point_intel in enumerate(plot_intel, start=1):
        prompt.line_break()
        prompt.text(f'Point #{i}:')
        prompt.text(f'Outline: {plot_point_intel.outline}')
        prompt.text(f'Description: {plot_point_intel.description}')

    return prompt