from typing import NewType, TypeAlias

from dandy.llm.prompt.prompt import Prompt

PromptOrStr: TypeAlias = Prompt | str
PromptOrStrOrNone: TypeAlias = Prompt | str | None