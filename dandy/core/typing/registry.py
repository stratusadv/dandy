from typing import Any

from dandy.core.typing.typing import TypedKwargsDict

TYPE_REGISTRY = {
    'TypedKwargsDict': TypedKwargsDict,
}


def resolve_type_from_registry(type_str: str) -> type:
    if type_str in TYPE_REGISTRY:
        return TYPE_REGISTRY[type_str.rsplit('.', maxsplit=1)[0]]

    return Any
