from dandy import Bot
from dandy.cli.actions.help.intelligence.intel.default_user_input_intel import DefaultUserInputIntel
from dandy.cli.actions.help.intelligence.prompt import default_user_input_bot_guidelines_prompt


class DefaultUserInputBot(Bot):
    role = 'Dandy CLI Helper'
    task = 'Read the user input and provide suggestions on how they can accomplish their task using this command line interface.'
    guidelines = default_user_input_bot_guidelines_prompt()
    intel_class = DefaultUserInputIntel

    def process(self, user_input: str) -> DefaultUserInputIntel:
        return self.llm.prompt_to_intel(
            prompt=user_input
        )
