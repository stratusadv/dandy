from __future__ import annotations


def get_image_format_from_base64_string(base64_string: str) -> str | None:
    return get_image_mime_type_from_base64_string(base64_string).split('/')[1]


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
