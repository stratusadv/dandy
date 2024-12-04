from dandy.workflow import Workflow
from example.pirate.monster.intel.bots.monster_llm_bots import MonsterNamingLlmBot, MonsterSelectionLlmBot
from example.pirate.monster.datasets import MONSTERS
from example.pirate.monster.models import SeaMonsterIntel


class SeaMonsterWorkflow(Workflow):
    @classmethod
    def process(cls, user_input: str) -> SeaMonsterIntel:
        monster_choice = MonsterSelectionLlmBot.process('I would like a random sea monster for a pirate adventure', MONSTERS)
        monster = monster_choice

        monster_name = MonsterNamingLlmBot.process(monster=monster)
        monster.name = monster_name

        return  monster
