from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from dandy.llm.intelligence.prompts import (
    service_system_prompt,
    service_user_prompt,
)

if TYPE_CHECKING:
    from dandy.llm.prompt.typing import PromptOrStrOrNone, PromptOrStr


def get_estimated_token_count_for_prompt(
        role: PromptOrStr,
        prompt: PromptOrStr,
        task: PromptOrStrOrNone = None,
        guidelines: PromptOrStrOrNone = None,
) -> int:
    return (
            service_system_prompt(
                role=role,
                task=task,
                guidelines=guidelines,
                system_override_prompt=None,
            ).estimated_token_count
            + service_user_prompt(prompt).estimated_token_count
    )


def get_image_mime_type_from_base64_string(base64_string: str) -> str | None:
    SIGNATURES = {
        'JVBERi0': 'application/pdf',
        'R0lGODdh': 'image/gif',
        'R0lGODlh': 'image/gif',
        'iVBORw0KGgo': 'image/png',
        '/9j/': 'image/jpg',
    }

    for signature in SIGNATURES:
        if base64_string.startswith(signature):
            return SIGNATURES[signature]

    return None


def get_audio_format_from_base64_string(base64_string: str) -> str | None:
    return get_audio_mime_type_from_base64_string(base64_string).split('/')[1]


def get_audio_mime_type_from_base64_string(base64_string: str) -> str | None:
    SIGNATURES = {
        'SUQzA': 'audio/mp3',
        'T2dnU': 'audio/ogg',
        'UklGR': 'audio/wav',
        'AAAAZ': 'audio/mp4',
    }

    for signature in SIGNATURES:
        if base64_string.startswith(signature):
            return SIGNATURES[signature]

    return None


def get_file_extension_from_url_string(url):
    parsed_url = urlparse(url)

    return Path(parsed_url.path).suffix.lower()[1:]
