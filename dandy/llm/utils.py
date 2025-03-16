from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Union

from dandy.llm.service.prompts import service_system_prompt, service_user_prompt

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


def get_estimated_token_count_for_prompt(
        prompt: Prompt,
        postfix_system_prompt: Union[Prompt, None] = None
) -> int:

    return service_system_prompt(
        system_prompt=postfix_system_prompt
    ).estimated_token_count + service_user_prompt(prompt).estimated_token_count


def get_image_mime_type_from_base64_string(base64_string):
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