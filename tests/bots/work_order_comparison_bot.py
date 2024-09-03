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
        .text('Your job is to compare the current work order with the list of existing work orders by following the rules below.')
        .unordered_list([
            'Use the description of the work orders for the comparison.'
            'Match work orders by the context of the description'
            'If the context is not closely related do not return that work order'
        ])
    )

    def process(self, current_work_order: WorkOrderModel) -> WorkOrderListModel:
        return self.process_prompt_to_model_object(
            prompt=(
                Prompt()
                .text('This is the current work order:')
                .model_object(current_work_order, triple_quote=True)
                .text('These are the existing work orders:')
                .model_object(ExistingWorkOrdersBot().process(), triple_quote=True)
            ),
            model=WorkOrderListModel
        )
