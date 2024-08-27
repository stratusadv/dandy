from typing import List

from pydantic import BaseModel


class WorkOrderModel(BaseModel):
    id: int
    equipment: str
    description: str


class WorkOrderListModel(BaseModel):
    work_orders: List[WorkOrderModel]