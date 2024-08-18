from dandy.llm.prompt import Prompt


def cartoon_character_prompt() -> Prompt:
    return (
        Prompt()
        .text('Create me a cartoon character')
        .title('Cartoon Character')
    )
