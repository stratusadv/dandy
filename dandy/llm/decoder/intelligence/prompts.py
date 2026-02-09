from dandy.llm.prompt.prompt import Prompt


def decoder_guidelines_prompt(
    keys_description: str,
    keyed_mapping_choices_dict: dict,
    max_return_values: int | None,
) -> Prompt:
    key_str = 'key' if max_return_values == 1 else 'keys'

    prompt = Prompt()

    guidelines = [
        f'Read through all of the "{keys_description}" dict values and return the numbered {key_str} that matches the values with information relevant to the user\'s request.',
    ]

    if max_return_values is not None and max_return_values > 0:
        if max_return_values == 1:
            guidelines.append(f'You must return exactly one numbered {key_str}.')
        else:
            guidelines.append(
                f'Return up to a maximum of {max_return_values} numbered {key_str}.'
            )
    else:
        guidelines.append(
            f"Return as many numbered {key_str} as you find that are relevant to the user's response."
        )

    guidelines.append(
        "Always return at least one numbered key closest to the user's request."
    )

    prompt.list(guidelines)

    prompt.line_break()
    prompt.heading(f'{keys_description} Dict')
    prompt.line_break()

    prompt.dict(keyed_mapping_choices_dict)

    return prompt


def decoder_max_key_count_error_prompt(returned_count: int, max_count: int) -> Prompt:
    return (
        Prompt()
        .text(
            'The response you provided exceeded the maximum number of keys you can return.'
        )
        .text(f'You returned {returned_count} keys.')
        .text(f'The maximum number of keys you can return is {max_count}.')
    )


def decoder_no_key_error_prompt() -> Prompt:
    return Prompt().text('The response you provided did not contain any keys.')
