from dandy.contrib.llm.bots.selector_llm_bot import SelectorLlmBot
from dandy.llm import Prompt
from dandy.llm.conf import llm_configs
from dandy.workflow import Workflow
from example.pirate.intelligence.prompts import pirate_story_prompt
from example.pirate.monster.intelligence.workflow.monster_generation_workflow import SeaMonsterWorkflow
from example.pirate.world.datasets import OCEANS
from example.pirate.ship.datasets import PIRATE_SHIPS
from example.pirate.crew.intelligence.bots.crew_generation_llm_bot import CrewGenerationLlmBot


class PirateStoryWorkflow(Workflow):
    @classmethod
    def process(cls, user_input: str) -> str:
        ocean_selection = SelectorLlmBot.process(
            Prompt('I would like a random ocean for a pirate adventure'),
            OCEANS.keys()
        )
        
        if ocean_selection.has_valid_choice:
            ocean = OCEANS[ocean_selection.items[0]]
        else:
            ocean = OCEANS['Pacific']

        ship_selection = SelectorLlmBot.process(
            Prompt('I would like a random ship for a pirate adventure'),
            PIRATE_SHIPS.keys()
        )

        if ship_selection.has_valid_choice:
            ship = PIRATE_SHIPS[ship_selection.items[0]]
        else:
            ship = PIRATE_SHIPS['ghostly_galleon']

        sea_monster = SeaMonsterWorkflow.process('N/A')

        crew = CrewGenerationLlmBot.process(
            'I would like my crew to be a dark and grumpy bunch of seasoned pirates'
        )

        ship.crew = crew

        return llm_configs.DEFAULT.assistant_str_prompt_to_str(
            pirate_story_prompt(
                ocean,
                ship,
                sea_monster
            ).to_str()
        )


class PirateStoryWithFuturesWorkflow(Workflow):
    @classmethod
    def process(cls, user_input: str) -> str:
        ocean_selection_future = SelectorLlmBot.process_to_future(
            Prompt('I would like a random ocean for a pirate adventure'),
            OCEANS.keys()
        )

        ship_selection_future = SelectorLlmBot.process_to_future(
            Prompt('I would like a random ship for a pirate adventure'),
            PIRATE_SHIPS.keys()
        )

        crew_future = CrewGenerationLlmBot.process_to_future(
            'I would like my crew to be a dark and grumpy bunch of seasoned pirates'
        )

        sea_monster_future = SeaMonsterWorkflow.process_to_future('N/A')

        if ocean_selection_future.result.has_valid_choice:
            ocean = OCEANS[ocean_selection_future.result.items[0]]
        else:
            ocean = OCEANS['Pacific']

        if ship_selection_future.result.has_valid_choice:
            ship = PIRATE_SHIPS[ship_selection_future.result.items[0]]
        else:
            ship = PIRATE_SHIPS['ghostly_galleon']

        ship.crew = crew_future.result

        return llm_configs.DEFAULT.assistant_str_prompt_to_str(
            pirate_story_prompt(
                ocean,
                ship,
                sea_monster_future.result
            ).to_str()
        )

