from typing import Any, Callable

from dandy.domain.tool.tool import BaseTool

QuestionHandler = Callable[[str, list[str]], str]


class QuestionTool(BaseTool):
    name = 'question'
    description = (
        'Ask the user a question and wait for their answer before continuing. '
        'Use this when you need a decision, preference, or confirmation that you '
        'cannot reasonably guess. When the answer is one of a few options, pass '
        'them as choices so the user can pick one by number; otherwise leave '
        "choices empty for a free-text answer. The returned text is the user's "
        'answer.'
    )

    action_label = 'Asking'

    NO_USER_ANSWER = (
        'No user is available to answer right now. Make a reasonable decision, '
        'state your assumption clearly, and proceed.'
    )

    def __init__(self, ask_user: QuestionHandler | None = None) -> None:
        self.ask_user = ask_user
        super().__init__()

    def action_output(self, **kwargs: Any) -> str | None:
        question = kwargs.get('question')
        return question if isinstance(question, str) and question else None

    def handle(self, question: str, choices: list[str] | None = None) -> str:
        if self.ask_user is None:
            return self.NO_USER_ANSWER

        return self.ask_user(question, list(choices or []))
