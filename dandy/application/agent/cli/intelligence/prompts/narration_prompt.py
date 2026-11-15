from dandy.domain.prompt.prompt import Prompt


def _narration_section(examples: list[str]) -> Prompt:
    return (
        Prompt()
        .sub_heading('Narration')
        .text(
            'Begin every message that calls a tool with one short, natural sentence '
            'narrating the step you are about to take. For example:',
            label='Narrate each tool call',
        )
        .list(examples, triple_backtick=True)
        .text('This narration is shown to the user as your running thoughts.')
    )
