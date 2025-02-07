from dandy.llm.bot import BaseLlmBot
from dandy.llm.prompt import Prompt
from example.pirate.monster.intelligence.intel import SeaMonsterNameIntel, SeaMonsterIntel


class MonsterNamingLlmBot(BaseLlmBot):
    config = 'LLAMA_3_1_8B'

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

        return cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .text(f'The user has provided the following monster:')
                .intel(monster, triple_quote=True)
            ),
            intel_class=SeaMonsterNameIntel
        ).name
