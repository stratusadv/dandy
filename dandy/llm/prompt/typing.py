from typing import NewType

from dandy.llm.prompt.prompt import Prompt

PromptOrStr = NewType('PromptOrStr', Prompt | str)
PromptOrStrOrNone = NewType('PromptOrStrOrNone', Prompt | str | None)