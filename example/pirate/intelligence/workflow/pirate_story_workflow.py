from dandy.llm.prompt import Prompt
from dandy.workflow import Workflow
from example.pirate.world.datasets import OCEANS
from example.pirate.world.intelligence.bots.ocean_selection_llm_bot import OceanSelectionLlmBot
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_2


class PirateStoryWorkflow(Workflow):
    @classmethod
    def process(cls, user_input: str) -> str:
        ocean_choice = OceanSelectionLlmBot.process('Select the Ocean with the biggest islands', OCEANS)

        if ocean_choice is None:
            ocean_choice = OceanSelectionLlmBot.process('I would like a random ocean for a pirate adventure', OCEANS)

        key, ocean = ocean_choice.popitem()


        return OLLAMA_LLAMA_3_2.service.assistant_str_prompt_to_str(str((
            Prompt()
            .text('Describe a pirate adventure in the following ocean:')
            .model_object(ocean, triple_quote=True)
        )))
