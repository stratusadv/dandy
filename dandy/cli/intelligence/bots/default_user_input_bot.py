from dandy import Bot, Prompt
from dandy.cli.actions.manager import ActionManager
from dandy.cli.intelligence.intel.default_user_input_intel import DefaultUserInputIntel

def default_user_input_bot_guidelines_prompt() -> Prompt:
    prompt = Prompt()

    prompt.text('Only use the information from the commands below to help the user.')
    prompt.text('If you cannot help the user, respond with "I do not know how to help you with that."')

    prompt.sub_heading('Commands')

    for command in ActionManager().actions:
        prompt.text(f'Name: {command.name} Command')
        prompt.text(f'Commands: {", ".join(command.input_calls)}')
        prompt.text(f'Description: {command.description}')

    return prompt


class DefaultUserInputBot(Bot):
    llm_role = 'Dandy CLI Helper'
    llm_task = 'Read the user input and provide suggestions on how they can accomplish their task'
    llm_guidelines = default_user_input_bot_guidelines_prompt()
    llm_intel_class = DefaultUserInputIntel

    def process(self, user_input: str) -> DefaultUserInputIntel:
        return self.llm.prompt_to_intel(
            prompt=user_input
        )
