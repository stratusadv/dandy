import json
import re


def extract_code_fence_json_body(response_text: str) -> str | None:
    """Return the body of a single fenced code block when it holds a JSON object.

    Live models sometimes wrap the final JSON answer in a markdown code fence
    (e.g. ```javascript```). When ``response_text`` contains exactly one fenced
    block and that block's body parses as JSON, return the body so callers can
    validate it against the target intel; otherwise return ``None``.
    """
    fence_pattern = re.compile(r'(?P<fence>`{3,}|~{3,})[^\n]*\n(?P<body>.*?)(?P=fence)', re.DOTALL)
    fence_blocks = list(fence_pattern.finditer(response_text))

    if len(fence_blocks) != 1:
        return None

    body = fence_blocks[0].group('body').strip()

    try:
        json.loads(body)
    except ValueError:
        return None

    return body
