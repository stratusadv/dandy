from dandy.llm.bot import BaseLlmBot
from dandy.llm.prompt import Prompt
from example.pirate.crew.intelligence.intel import CrewIntel


class CrewGenerationLlmBot(BaseLlmBot):
    instructions_prompt = (
        Prompt()
        .text('You are a pirate crew generation bot.')
        .text('Your job is to generate a pirate crew for the user.')
        .text('Using the following rules generate a crew.')
        .unordered_list([
            'The crew must have at least one of each role.',
            'Generate a minimum of 6 crew members.',
        ])
    )

    @classmethod
    def process(cls, crew_description: str) -> CrewIntel:
        return cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .text('The user has provided the following crew description:')
                .text(crew_description)
            ),
            intel_class=CrewIntel
        )
