import os
from enum import Enum

from dandy.contrib.bots import SingleChoiceLlmBot, MultipleChoiceLlmBot
from dandy.contrib.bots.choice_llm_bot import MultipleChoiceResponse
from dandy.llm.tests.configs import OLLAMA_LLAMA_3_1
from tests.bots.work_order_comparison_bot import WorkOrderComparisonBot
from tests.factories import generate_current_work_order


# matching_work_orders = WorkOrderComparisonBot.process(generate_current_work_order())
#
# print(matching_work_orders.model_dump_json(indent=4))

class Stuff(Enum):
    food = 'food'
    dinosaurs = 'dinosaurs'
    birds = 'birds'
    gasoline = 'gasoline'
    tacos = 'tacos'
    eating = 'eating out'


stuff_dict = {
    'food': 'food_val',
    'dinosaurs': 'dinosaurs_val',
    'birds': 'birds_val',
    'gasoline': 'gasoline_val',
    'tacos': 'tacos_val',
    'eating': 'eating_out_val'
}


stuff_list = [
    'food',
    'dinosaurs',
    'birds',
    'gasoline',
    'tacos',
    'eating out'
]


MultipleChoiceLlmBot.llm_config = OLLAMA_LLAMA_3_1

choice = MultipleChoiceLlmBot.process(
    user_input='I want to get tacos for lunch today',
    choices=stuff_list,
)

print(choice)
