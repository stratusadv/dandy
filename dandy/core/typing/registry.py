from typing import Any

from dandy.core.typing.typing import TypedKwargsDict
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone

TYPE_REGISTRY = {
    'PromptOrStr': PromptOrStr,
    'PromptOrStrOrNone': PromptOrStrOrNone,
    'TypedKwargsDict': TypedKwargsDict,
}


def resolve_type_from_registry(type_str: str) -> type:
    if type_str in TYPE_REGISTRY:
        return TYPE_REGISTRY[type_str.split('.')[-1]]

    return Any
