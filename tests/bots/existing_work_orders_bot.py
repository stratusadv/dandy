from typing import Any

from dandy.bot import Bot
from tests.factories import generate_existing_work_order_list
from tests.models.work_order_models import WorkOrderListModel


class ExistingWorkOrdersBot(Bot):
    def process(self) -> WorkOrderListModel:
        return generate_existing_work_order_list()
