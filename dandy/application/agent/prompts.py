from dandy.domain.prompt.prompt import Prompt


def continuation_prompt() -> Prompt:
    return Prompt().text(
        'Continue working on the request. The conversation above contains the '
        'original request and your previous turns. Keep using your tools as '
        'needed. When the request is fully complete, set "done" to true in your '
        'response; otherwise keep "done" false and say what you did this turn '
        'and what remains.'
    )
