from typing import List

from dandy.schema import Schema


class WorkOrderSchema(Schema):
    id: int
    equipment: str
    description: str


class ExistingWorkOrderListSchema(Schema):
    work_orders: List[WorkOrderSchema]