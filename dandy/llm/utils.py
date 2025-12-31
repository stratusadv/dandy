from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    pass


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
