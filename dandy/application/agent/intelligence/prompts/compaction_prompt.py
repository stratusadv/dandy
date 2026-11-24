from dandy.domain.prompt.prompt import Prompt


def compaction_prompt(conversation_text: str) -> Prompt:
    return (
        Prompt()
        .text(
            'Summarize the earlier part of this coding conversation so the work can '
            'continue without the full transcript. Preserve the goal, key decisions '
            'and findings, files touched and what changed, commands run and their '
            'outcomes, errors and how they were fixed, pending tasks, the current '
            'work, and the next step. Drop redundant tool output and chit-chat. '
            'Refer to files by path. Keep each item to one short line.'
        )
        .text('The conversation is between the delimiter lines below.')
        .text('--- BEGIN CONVERSATION ---')
        .text(conversation_text)
        .text('--- END CONVERSATION ---')
    )
