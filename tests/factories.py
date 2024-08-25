from tests.models.work_order_models import WorkOrderModel, ExistingWorkOrderListModel


def generate_current_work_order() -> WorkOrderModel:
    return WorkOrderModel(
        id=1234,
        equipment='equipment_1',
        description='I am finding cheese and spicy beef in the gears'
    )


def generate_existing_work_order_list() -> ExistingWorkOrderListModel:
    return ExistingWorkOrderListModel(
        work_orders=[
            WorkOrderModel(
                id=456,
                equipment='equipment_1',
                description='there is a taco stuck in the machine'
            ),
            WorkOrderModel(
                id=22,
                equipment='equipment_1',
                description='the machine has caught fire'
            ),
            WorkOrderModel(
                id=989,
                equipment='equipment_1',
                description='Every time I eat my lunch by the machine it stops running'
            )
        ]
    )