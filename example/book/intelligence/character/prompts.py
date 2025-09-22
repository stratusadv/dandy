from dandy import Prompt
from example.book.intelligence.character.intel import CharactersIntel


def characters_intel_prompt(characters_intel: CharactersIntel) -> Prompt:
    prompt = Prompt()

    prompt.heading('Characters:')

    for character in characters_intel:
        prompt.text(label='First Name', text=character.first_name)
        prompt.text(label='Last Name', text=character.last_name)
        prompt.text(label='Age', text=str(character.age))
        prompt.text(label='Nickname', text=character.nickname)
        prompt.text(label='Description', text=character.description)
        prompt.text(label='Type', text=character.type.value)
        prompt.text(label='Alignment', text=character.alignment.value)

        prompt.line_break()

    return prompt
