from dandy.bot import LlmBot
from dandy.llm.prompt import Prompt
from tests.models.work_order_models import WorkOrderModel, WorkOrderListModel
from tests.bots.existing_work_orders_bot import ExistingWorkOrdersBot


class WorkOrderComparisonBot(LlmBot):
    role_prompt = (
        Prompt()
        .text('You\'re a work order comparison agent.')
    )

    instructions_prompt = (
        Prompt()
        .text('Your job is to look at the current work order description and review it against the list of existing work orders descriptions for related context and return any existing work orders that have a related context.')
    )

    def process(self, current_work_order: WorkOrderModel) -> WorkOrderListModel:
        return self.process_prompt_to_model_object(
            prompt=(
                Prompt()
                .text('This is the current work order:')
                .model_object(current_work_order)
                .text('These are the existing work orders:')
                .model_object(ExistingWorkOrdersBot().process())
            ),
            model=WorkOrderListModel
        )
