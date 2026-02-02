from __future__ import annotations


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
