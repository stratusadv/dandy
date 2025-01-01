from dandy.bot import LlmBot
from dandy.contrib.bots import SingleChoiceLlmBot
from dandy.llm.prompt import Prompt
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1_8B
from example.pirate.monster.intel import SeaMonsterNameStructureIntel, SeaMonsterIntel


class MonsterSelectionLlmBot(SingleChoiceLlmBot):
    role_prompt = Prompt().text('You are an monster selection bot.')
    config = OLLAMA_LLAMA_3_1_8B
    temperature = 0.0



class MonsterNamingLlmBot(LlmBot):
    temperature = 0.7
    config = OLLAMA_LLAMA_3_1_8B

    role_prompt = Prompt().text('You are an monster selection bot.')

    instructions_prompt = (
        Prompt()
        .text('Your job is to name the following monster.')
        .text('Your response should only contain the name you have chosen.')
        .text('The name you have chose can not have any apostrophes.')
    )

    @classmethod
    def process(cls, monster: SeaMonsterIntel) -> str:
        prompt = (
            Prompt()
            .text('Your job is to name the following monster.')
        )

        return super().process_prompt_to_model_object(
            prompt=Prompt()
            .text(f'The user has provided the following monster:')
            .model_object(monster, triple_quote=True),
            model=SeaMonsterNameStructureIntel
        ).name
