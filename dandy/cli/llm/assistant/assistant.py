from dandy.llm import LlmBot

def assistant(
        llm_config: str,
        user_prompt: str,
) -> None:

    LlmBot.config = llm_config

    if user_prompt:
        user_input = user_prompt
    else:
        user_input = input(f'Assistant Prompt: ')

    print(f'Prompting Assistant ... depending on your llm configuration this may take up to a couple minutes')

    response = LlmBot.process(
        prompt=user_input
    )

    if response:
        print(response.text)

    else:
        print('Failed to get response from the assistant ... try again')
