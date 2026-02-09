from __future__ import annotations

from dandy.file.audio.constants import BASE64_AUDIO_MIME_SIGNATURES
from dandy.file.exceptions import FileRecoverableError


def get_audio_format_from_base64_string(base64_string: str) -> str:
    return get_audio_mime_type_from_base64_string(base64_string).split('/')[1]


def get_audio_mime_type_from_base64_string(base64_string: str) -> str:

    for signature in BASE64_AUDIO_MIME_SIGNATURES:
        if base64_string.startswith(signature):
            return BASE64_AUDIO_MIME_SIGNATURES[signature]

    message = 'Unable to determine audio format from base64 string'
    raise FileRecoverableError(message)
