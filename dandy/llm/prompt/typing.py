from typing_extensions import NewType

from dandy.llm.prompt.prompt import Prompt

PromptOrStr = NewType('PromptOrStr', Prompt | str)
PromptOrStrOrNone = NewType('PromptOrStrOrNone', Prompt | str | None)