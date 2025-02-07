from dandy.llm.service.config import BaseLlmConfig


def assistant(
        llm_config: BaseLlmConfig,
        user_prompt: str,
) -> None:

    if user_prompt:
        user_input = user_prompt
    else:
        user_input = input(f'Assistant Prompt: ')

    print(f'Prompting Assistant ... depending on your llm configuration this may take up to a couple minutes')

    response = llm_config.service.assistant_str_prompt_to_str(
        user_prompt_str=user_input
    )

    if response:
        print(response)

    else:
        print('Failed to get response from the assistant ... try again')
