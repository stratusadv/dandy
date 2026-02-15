from dandy import Prompt
from dandy.cli.actions.constants import ACTIONS


def default_user_input_bot_guidelines_prompt() -> Prompt:
    prompt = Prompt()

    prompt.text('Only use the information from the commands below to help the user.')
    prompt.text('Make suggestions of commands that will help the user or get them started.')
    prompt.text('If they seem lost suggest they start with the "explain" command.')
    prompt.text('If you cannot help the user, respond with "I do not know how to help you with that."')

    prompt.sub_heading('Commands')

    for command in ACTIONS:
        prompt.text(f'Name: {command.name} Command')
        prompt.text(f'Commands: {", ".join(command.input_calls)}')
        prompt.text(f'Description: {command.description}')

    prompt.text(f'Name: Help Command')
    prompt.text(f'Commands: {", ".join(["/h", "/help"])}')
    prompt.text(f'Description: "how to use this the dandy command line interface."')

    return prompt