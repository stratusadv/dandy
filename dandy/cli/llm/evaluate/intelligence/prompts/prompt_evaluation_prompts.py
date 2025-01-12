from dandy.llm import Prompt


def evaluate_prompt_system_prompt() -> Prompt:
    return (
        Prompt()
        .title(
            'Your a prompt evaluator that needs to review the users prompts and determine if there is improvements you can suggest')
        .divider()
        .text(
            'Follow the rules below and the provided code to create a llm bot based on the users input')
        .list([
            'Use the provided source code to evaluate improvements to the users source code'
        ])
        .line_break()
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
        .text(prompt_description)
        .line_break()
        .text(
            prompt_source,
            triple_quote=True,
            triple_quote_label=prompt_name
        )
    )
