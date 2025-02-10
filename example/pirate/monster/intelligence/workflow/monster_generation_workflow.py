from dandy.contrib.llm.bots.selector_llm_bot import SelectorLlmBot
from dandy.llm import Prompt
from dandy.workflow import BaseWorkflow
from example.pirate.monster.intelligence.bots.monster_llm_bots import MonsterNamingLlmBot
from example.pirate.monster.datasets import MONSTERS
from example.pirate.monster.intelligence.intel import SeaMonsterIntel


class SeaMonsterWorkflow(BaseWorkflow):
    @classmethod
    def process(cls, user_input: str) -> SeaMonsterIntel:
        monster_selection = SelectorLlmBot.process(Prompt('I would like a random sea monster for a pirate adventure'), MONSTERS)
        
        if monster_selection.has_valid_choice:
            monster = MONSTERS[monster_selection.items[0]]
        else:
            monster = MONSTERS['kraken']

        monster_name = MonsterNamingLlmBot.process(monster=monster)
        monster.name = monster_name

        return  monster
