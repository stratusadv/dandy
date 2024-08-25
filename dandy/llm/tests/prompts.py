from dandy.llm.prompt import Prompt


def cartoon_character_prompt() -> Prompt:
    return (
        Prompt()
        .text('Create me a random and old timey cartoon character')
    )
