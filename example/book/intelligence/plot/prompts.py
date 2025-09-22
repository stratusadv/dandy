from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt

if TYPE_CHECKING:
    from example.book.intelligence.plot.intel import PlotIntel


def plot_intel_prompt(plot_intel: PlotIntel) -> Prompt:
    prompt = Prompt()
    prompt.heading('Plot Points:')

    for i, plot_point_intel in enumerate(plot_intel, start=1):
        prompt.line_break()
        prompt.sub_heading(f'Point #{i}:')
        prompt.text(label='Outline', text=plot_point_intel.outline)
        prompt.text(label='Description', text=plot_point_intel.description)

    return prompt
