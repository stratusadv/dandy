import os
from enum import Enum

from dandy.contrib.bots import SingleChoiceLlmBot, MultipleChoiceLlmBot
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



choice = SingleChoiceLlmBot.process(
    user_input='I want to get tacos for lunch',
    choices=Stuff,
)

print(choice)