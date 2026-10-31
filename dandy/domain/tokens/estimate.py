# Per-character token costs fitted against a BPE tokenizer over representative
# Python code, JSON, prose, and markdown. Letters tokenize at roughly 4.5
# characters per token, digits and symbols at 2-1.5 per token, and whitespace
# costs almost nothing. The previous flat character-per-token rate ignored
# content type, which under-counted symbol-heavy payloads and over-counted prose.

TOKEN_COUNT_FIXED_BASE = 3

TOKEN_COUNT_ALPHA_CHAR_COST = 0.215
TOKEN_COUNT_DIGIT_CHAR_COST = 0.5
TOKEN_COUNT_SYMBOL_CHAR_COST = 0.67
TOKEN_COUNT_SPACE_CHAR_COST = 0.02
TOKEN_COUNT_OTHER_CHAR_COST = 0.5

# Chat-template framing: every message carries role markers around its content.

TOKEN_COUNT_ROLE_OVERHEAD = 4

# Tool use framing: an assistant tool-call declaration and the reference back to
# it on the matching tool result.

TOKEN_COUNT_TOOL_CALL_OVERHEAD = 8
TOKEN_COUNT_TOOL_CALL_ID_OVERHEAD = 3

# Image tokens as documented for the OpenAI vision API: low detail is a fixed
# cost, high detail is a base cost plus a per-tile cost. With no dimensions
# available the tile count defaults to a 1024x1024 equivalent, and 'auto' is
# treated as high to stay conservative.

TOKEN_COUNT_IMAGE_LOW = 85
TOKEN_COUNT_IMAGE_TILE = 170
TOKEN_COUNT_IMAGE_TILE_DEFAULT_COUNT = 4
TOKEN_COUNT_IMAGE_HIGH_DEFAULT = TOKEN_COUNT_IMAGE_LOW + (
    TOKEN_COUNT_IMAGE_TILE * TOKEN_COUNT_IMAGE_TILE_DEFAULT_COUNT
)


def get_estimated_token_count_for_string(string: str) -> int:
    if not string:
        return 0

    alpha_count = 0
    digit_count = 0
    symbol_count = 0
    space_count = 0
    other_count = 0

    for character in string:
        if not character.isascii():
            other_count += 1
        elif character.isalpha():
            alpha_count += 1
        elif character.isdigit():
            digit_count += 1
        elif character.isspace():
            space_count += 1
        else:
            symbol_count += 1

    token_count = (
        TOKEN_COUNT_FIXED_BASE
        + (alpha_count * TOKEN_COUNT_ALPHA_CHAR_COST)
        + (digit_count * TOKEN_COUNT_DIGIT_CHAR_COST)
        + (symbol_count * TOKEN_COUNT_SYMBOL_CHAR_COST)
        + (space_count * TOKEN_COUNT_SPACE_CHAR_COST)
        + (other_count * TOKEN_COUNT_OTHER_CHAR_COST)
    )

    return int(token_count)


def get_estimated_token_count_for_image(detail: str) -> int:
    if detail == 'low':
        return TOKEN_COUNT_IMAGE_LOW
    return TOKEN_COUNT_IMAGE_HIGH_DEFAULT


def get_estimated_token_count_for_audio(base64_string: str) -> int:
    return get_estimated_token_count_for_string(base64_string)


def get_estimated_token_count_for_tool_calls(tool_calls: list[dict]) -> int:
    token_count = TOKEN_COUNT_TOOL_CALL_OVERHEAD * len(tool_calls)

    for tool_call in tool_calls:
        token_count += get_estimated_token_count_for_string(tool_call.get('id') or '')

        function = tool_call.get('function') or {}
        token_count += get_estimated_token_count_for_string(function.get('name') or '')

        arguments = function.get('arguments')

        if isinstance(arguments, dict):
            arguments = str(arguments)

        if arguments:
            token_count += get_estimated_token_count_for_string(arguments)

    return token_count
