from dandy.llm import Prompt


def generate_llm_bot_system_prompt() -> Prompt:
    return (
        Prompt()
        .title("Your a coder that needs to write a large language model bot using the dandy framework.")
        .divider()
        .text(
            'Follow the rules below and the provided code to create a llm bot based on the users input')
        .list([
            'Your llm bot must inherit the Abstract LlmBot class in the code.'
            'Add a Pydantic model that the Llm Bot can used in the output.',
            'The instructions prompt should be detailed an utilize the Prompt class thoroughly to make a good prompt.',
            'Do not include the model schema in the instructions prompt as that is handled by the process_prompt_to_model_object method.',
            'The new llm bot must use the process method for all its logic and can call the process_prompt_to_model_object for llm interactions.',
            'Return only python code in a string with no triple quotes or explanations as this code will be used directly in a python file to be run.',
            'Make sure to be explict with the keyword arguments in the process method.',
            'the file name for this bot should end in "_llm_bot" with the extension ".py"',
        ])
        .line_break()
        .module_source('dandy.llm.prompt.prompt')
        .line_break()
        .module_source('dandy.handler.handler')
        .line_break()
        .module_source('dandy.bot.bot')
        .line_break()
        .module_source('dandy.bot.llm_bot')
        .line_break()
    )


def generate_llm_bot_user_prompt(user_input: str) -> Prompt:
    return (
        Prompt()
        .text(user_input)
    )
