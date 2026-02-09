from __future__ import annotations

from dandy.file.exceptions import FileRecoverableError
from dandy.file.image.constants import BASE64_IMAGE_MIME_SIGNATURES


def get_image_format_from_base64_string(base64_string: str) -> str | None:
    return get_image_mime_type_from_base64_string(base64_string).split('/')[1]


def get_image_mime_type_from_base64_string(base64_string: str) -> str | None:

    for signature in BASE64_IMAGE_MIME_SIGNATURES:
        if base64_string.startswith(signature):
            return BASE64_IMAGE_MIME_SIGNATURES[signature]

    message = 'Unable to determine image format from base64 string'
    raise FileRecoverableError(message)
