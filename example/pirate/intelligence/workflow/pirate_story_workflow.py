from dandy.llm.prompt import Prompt
from dandy.workflow import Workflow
from example.pirate.crew.datasets import CREW_MEMBERS
from example.pirate.monster.workflow.monster_generation_workflow import SeaMonsterWorkflow
from example.pirate.world.datasets import OCEANS
from example.pirate.world.intelligence.bots.ocean_selection_llm_bot import OceanSelectionLlmBot
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_2
from example.pirate.ship.intelligence.bots.ship_selection_llm_bot import PirateShipSelectionLlmBot
from example.pirate.ship.datasets import PIRATE_SHIPS
from example.pirate.crew.intelligence.bots.crew_selection_llm_bot import CrewSelectionLlmBot


class PirateStoryWorkflow(Workflow):
    @classmethod
    def process(cls, user_input: str) -> str:
        # ocean_choice = OceanSelectionLlmBot.process('Select the Ocean with the biggest islands', OCEANS)

        # if ocean_choice is None:
        ocean_choice = OceanSelectionLlmBot.process('I would like a random ocean for a pirate adventure', OCEANS)
        ocean = ocean_choice
        ship_choice = PirateShipSelectionLlmBot.process('I would like a random ship for a pirate adventure', PIRATE_SHIPS)
        ship = ship_choice

        sea_monster = SeaMonsterWorkflow.process('N/A')

        crew_choices = CrewSelectionLlmBot.process('I would like a random selection of exactly one captain, one navigator, and one engineer.', CREW_MEMBERS)

        ship.crew_members = crew_choices

        return OLLAMA_LLAMA_3_2.service.assistant_str_prompt_to_str(str((
            Prompt()
            .text('Describe a pirate adventure in the following ocean:')
            .model_object(ocean, triple_quote=True)
            .text('With the following ship:')
            .model_object(ship, triple_quote=True)
            .text('That has to face this sea monster:')
            .model_object(sea_monster, triple_quote=True)
        )))
