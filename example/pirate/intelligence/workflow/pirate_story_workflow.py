from dandy.llm.prompt import Prompt
from dandy.workflow import Workflow
from example.pirate.intelligence.prompts import pirate_story_prompt
from example.pirate.monster.workflow.monster_generation_workflow import SeaMonsterWorkflow
from example.pirate.world.datasets import OCEANS
from example.pirate.world.intelligence.bots.ocean_selection_llm_bot import OceanSelectionLlmBot
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_2_3B, OLLAMA_LLAMA_3_1_8B
from example.pirate.ship.intelligence.bots.ship_selection_llm_bot import ShipSelectionLlmBot
from example.pirate.ship.datasets import PIRATE_SHIPS
from example.pirate.crew.intelligence.bots.crew_generation_llm_bot import CrewGenerationLlmBot


class PirateStoryWorkflow(Workflow):
    @classmethod
    def process(cls, user_input: str) -> str:
        ocean = OceanSelectionLlmBot.process(
            'I would like a random ocean for a pirate adventure',
            OCEANS
        )

        ship = ShipSelectionLlmBot.process(
            'I would like a random ship for a pirate adventure',
            PIRATE_SHIPS
        )

        sea_monster = SeaMonsterWorkflow.process('N/A')

        crew = CrewGenerationLlmBot.process(
            'I would like my crew to be a dark and grumpy bunch of seasoned pirates'
        )

        ship.crew = crew

        return OLLAMA_LLAMA_3_1_8B.assistant_str_prompt_to_str(
            pirate_story_prompt(
                ocean,
                ship,
                sea_monster
            ).to_str()
        )


class PirateStoryWithFuturesWorkflow(Workflow):
    @classmethod
    def process(cls, user_input: str) -> str:
        ocean_future = OceanSelectionLlmBot.process_to_future(
            'I would like a random ocean for a pirate adventure',
            OCEANS
        )

        ship_future = ShipSelectionLlmBot.process_to_future(
            'I would like a random ship for a pirate adventure',
            PIRATE_SHIPS
        )

        sea_monster_future = SeaMonsterWorkflow.process_to_future('N/A')

        crew_future = CrewGenerationLlmBot.process_to_future(
            'I would like my crew to be a happy and future thinking bunch of unskilled pirates'
        )

        ship = ship_future.result

        ship.crew = crew_future.result

        return OLLAMA_LLAMA_3_1_8B.assistant_str_prompt_to_str(
            pirate_story_prompt(
                ocean_future.result,
                ship,
                sea_monster_future.result,
            ).to_str()
        )
