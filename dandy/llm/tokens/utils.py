from dandy.consts import ESTIMATED_CHARACTERS_PER_TOKEN


def get_estimated_token_count_for_string(string: str) -> int:
    return int(len(string) / ESTIMATED_CHARACTERS_PER_TOKEN)