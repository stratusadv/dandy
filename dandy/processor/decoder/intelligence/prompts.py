from dandy.llm.prompt.prompt import Prompt


def decoder_max_key_count_error_prompt(
        returned_count: int,
        max_count: int
) -> Prompt:
    return (
        Prompt()
        .text('The response you provided exceeded the maximum number of keys you can return.')
        .text(f'You returned {returned_count} keys.')
        .text(f'The maximum number of keys you can return is {max_count}.')
    )

def decoder_no_key_error_prompt() -> Prompt:
    return (
        Prompt()
        .text('The response you provided did not contain any keys.')
    )
