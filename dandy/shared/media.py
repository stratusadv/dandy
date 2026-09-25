from __future__ import annotations

from dandy.shared.exceptions import FileRecoverableError

BASE64_AUDIO_MIME_SIGNATURES = {
    'SUQzA': 'audio/mp3',
    '//': 'audio/mp3',
    'T2dnU': 'audio/ogg',
    'UklGR': 'audio/wav',
    'AAAAZ': 'audio/mp4',
    '//O': 'audio/mp4',
}

BASE64_IMAGE_MIME_SIGNATURES = {
    'JVBERi0': 'application/pdf',
    'R0lGODdh': 'image/gif',
    'R0lGODlh': 'image/gif',
    'iVBORw0KGgo': 'image/png',
    '/9j/': 'image/jpg',
}


def get_audio_format_from_base64_string(base64_string: str) -> str:
    return get_audio_mime_type_from_base64_string(base64_string).split('/')[1]


def get_audio_mime_type_from_base64_string(base64_string: str) -> str:

    for signature in BASE64_AUDIO_MIME_SIGNATURES:
        if base64_string.startswith(signature):
            return BASE64_AUDIO_MIME_SIGNATURES[signature]

    message = 'Unable to determine audio format from base64 string'
    raise FileRecoverableError(message)


def get_image_format_from_base64_string(base64_string: str) -> str | None:
    return get_image_mime_type_from_base64_string(base64_string).split('/')[1]


def get_image_mime_type_from_base64_string(base64_string: str) -> str | None:

    for signature in BASE64_IMAGE_MIME_SIGNATURES:
        if base64_string.startswith(signature):
            return BASE64_IMAGE_MIME_SIGNATURES[signature]

    message = 'Unable to determine image format from base64 string'
    raise FileRecoverableError(message)
