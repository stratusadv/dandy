from dandy.llm import Prompt
from example.book.intelligence.character.intel import CharactersIntel


def characters_intel_prompt(characters_intel: CharactersIntel) -> Prompt:
    prompt = Prompt()

    prompt.text('Characters:')

    for character in characters_intel.characters:
        prompt.line_break()

        prompt.text(f'First Name: {character.first_name}')
        prompt.text(f'Last Name: {character.last_name}')
        prompt.text(f'Age: {character.age}')
        prompt.text(f'Nickname: {character.nickname}')
        prompt.text(f'Description: {character.description}')
        prompt.text(f'Type: {character.type.value}')
        prompt.text(f'Alignment: {character.alignment.value}')

    return prompt
