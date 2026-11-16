from __future__ import annotations

from dandy.shared.exceptions import FileUsageError

_BASE64_AUDIO_MIME_SIGNATURES = {
    'SUQzA': 'audio/mp3',
    '//': 'audio/mp3',
    'T2dnU': 'audio/ogg',
    'UklGR': 'audio/wav',
    'AAAAZ': 'audio/mp4',
    '//O': 'audio/mp4',
}

_BASE64_IMAGE_MIME_SIGNATURES = {
    'JVBERi0': 'application/pdf',
    'R0lGODdh': 'image/gif',
    'R0lGODlh': 'image/gif',
    'iVBORw0KGgo': 'image/png',
    '/9j/': 'image/jpg',
}


def get_audio_format_from_base64_string(base64_string: str) -> str:
    return get_audio_mime_type_from_base64_string(base64_string).split('/')[1]


def get_audio_mime_type_from_base64_string(base64_string: str) -> str:

    for signature, mime_type in _BASE64_AUDIO_MIME_SIGNATURES.items():
        if base64_string.startswith(signature):
            return mime_type

    message = 'Unable to determine audio format from base64 string'
    raise FileUsageError(message)


def get_image_format_from_base64_string(base64_string: str) -> str:
    return get_image_mime_type_from_base64_string(base64_string).split('/')[1]


def get_image_mime_type_from_base64_string(base64_string: str) -> str:

    for signature, mime_type in _BASE64_IMAGE_MIME_SIGNATURES.items():
        if base64_string.startswith(signature):
            return mime_type

    message = 'Unable to determine image format from base64 string'
    raise FileUsageError(message)
