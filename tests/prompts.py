from dandy.llm.prompt import Prompt


def business_idea_input_prompt() -> Prompt:
    return (
        Prompt()
        .text('Poetry Service')
    )
