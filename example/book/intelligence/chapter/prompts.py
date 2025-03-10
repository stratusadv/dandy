from dandy.llm import Prompt
from example.book.intelligence.chapter.intel import ChaptersIntel, ChapterIntel


def chapter_intel_overview_prompt(chapter_intel: ChapterIntel) -> Prompt:
    prompt = Prompt()
    prompt.text(f'Title: {chapter_intel.title}')
    prompt.text(f'Covered Plot Points: {chapter_intel.covered_plot_points}')
    if chapter_intel.scenes:
        prompt.line_break()
        prompt.text('Scenes:')
        prompt.list([scene_intel.summary for scene_intel in chapter_intel.scenes])

    return prompt


def chapter_intel_prompt(chapter_intel: ChapterIntel) -> Prompt:
    return (
        Prompt()
        .prompt(chapter_intel_overview_prompt(chapter_intel))
        .text(f'Content: {chapter_intel.content}')
    )


def chapters_intel_prompt(chapters_intel: ChaptersIntel) -> Prompt:
    prompt = Prompt()

    for chapter_intel in chapters_intel.chapters:
        prompt.line_break()
        prompt.prompt(chapter_intel_prompt(chapter_intel))

    return prompt
