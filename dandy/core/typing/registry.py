from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone

TYPE_REGISTRY = {
    'PromptOrStr': PromptOrStr,
    'PromptOrStrOrNone': PromptOrStrOrNone,
}

def resolve_type_from_registry(type_str) -> type:
    if type_str in TYPE_REGISTRY:
        return TYPE_REGISTRY[type_str]
    else:
        return type(None)