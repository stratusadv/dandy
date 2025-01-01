from dandy.bot import LlmBot
from dandy.llm.prompt import Prompt
from example.pirate.crew.intelligence.intel import CrewIntel
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1_8B


class CrewGenerationLlmBot(LlmBot):
    instructions_prompt = (
        Prompt()
        .text('You are a pirate crew generation bot.')
        .text('Your job is to generate a pirate crew for the user.')
        .text('Using the following rules generate a crew.')
        .unordered_list([
            'The crew must have at least one of each role.',
            'Generate a minimum of 5 crew members.',
        ])
    )
    config = OLLAMA_LLAMA_3_1_8B
    temperature = 0.2

    @classmethod
    def process(cls, crew_description: str) -> CrewIntel:
        return cls.process_prompt_to_model_object(
            prompt=(
                Prompt()
                .text('The user has provided the following crew description:')
                .text(crew_description)
            ),
            model=CrewIntel
        )
