from typing import Any

from dandy.tool.tool import Tool
from tests.factories import generate_existing_work_order_list
from tests.models.work_order_models import WorkOrderListModel


class ExistingWorkOrdersTool(Tool):
    def validate_input_data(self, input_data: int) -> bool:
        if isinstance(input_data, int):
            return True

        return False

    def process_input_data(self) -> WorkOrderListModel:
        return generate_existing_work_order_list()
