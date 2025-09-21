from __future__ import annotations

from dandy.llm.prompt.typing import PromptOrStrOrNone, PromptOrStr
from dandy.llm.service.intelligence.prompts import service_system_prompt, service_user_prompt


def get_estimated_token_count_for_prompt(
        prompt: PromptOrStr,
        postfix_system_prompt: PromptOrStrOrNone = None
) -> int:

    return service_system_prompt(
        system_prompt=postfix_system_prompt
    ).estimated_token_count + service_user_prompt(prompt).estimated_token_count


def get_image_mime_type_from_base64_string(base64_string) -> str | None:
    SIGNATURES = {
        "JVBERi0": "application/pdf",
        "R0lGODdh": "image/gif",
        "R0lGODlh": "image/gif",
        "iVBORw0KGgo": "image/png",
        "/9j/": "image/jpg"
    }

    for signature in SIGNATURES:
        if base64_string.startswith(signature):
            return SIGNATURES[signature]

    return None