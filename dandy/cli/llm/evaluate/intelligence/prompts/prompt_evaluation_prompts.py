from dandy.llm import Prompt


def evaluate_prompt_system_prompt() -> Prompt:
    return (
        Prompt()
        .title(
            'Your a prompt evaluator that needs to review the users prompts and determine if there is improvements you can suggest.')
        .divider()
        .text(
            'Follow the rules below and the provided updated code.')
        .list([
            'Use the provided module source code to understand the users prompt code.',
            'With the prompt description provided by the user update the code to improve its chance to work with an large language model.',
            'Add lines of code to the prompt if needed to improve its chance to work with an large language model.'
        ])
        .line_break()
        .heading('This is the module source code used to create the prompt.')
        .module_source('dandy.llm.prompt.prompt')
        .line_break()
    )


def evaluate_prompt_user_prompt(
        prompt_name: str,
        prompt_source: str,
        prompt_description: str,
) -> Prompt:
    return (
        Prompt()
        .heading('Prompt Description')
        .text(prompt_description)
        .line_break()
        .heading('Prompt Source Code')
        .text(
            prompt_source,
            triple_quote=True,
            triple_quote_label=prompt_name
        )
    )
