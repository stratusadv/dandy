from typing import Any

from dandy.agent import Agent
from dandy.llm.prompt import Prompt
from tests.models.work_order_models import WorkOrderModel, WorkOrderListModel
from tests.tools.existing_work_orders_tool import ExistingWorkOrdersTool

class WorkOrderComparisonAgent(Agent):
    role_prompt = (
        Prompt()
        .text('You\'re a work order comparison agent.')
    )

    instructions_prompt = (
        Prompt()
        .text('Your job is to look at the current work order description and review it against the list of existing work orders descriptions for related context and return any existing work orders that have a related context.')
    )

    def process_input_data(self) -> WorkOrderListModel:
        return self.process_prompt_to_model_object(
            prompt=(
                Prompt()
                .text('This is the current work order:')
                .model_object(self.input_data)
                .text('These are the existing work orders:')
                .model_object(ExistingWorkOrdersTool.run(1))
            ),
            model=WorkOrderListModel
        )


    def validate_input_data(self, input_data: WorkOrderModel) -> bool:
        if isinstance(input_data, WorkOrderModel):
            return True

        return False
