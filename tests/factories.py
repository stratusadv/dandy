from tests.models.work_order_models import WorkOrderModel, WorkOrderListModel


def generate_current_work_order() -> WorkOrderModel:
    return WorkOrderModel(
        id=1234,
        equipment='equipment_1',
        description='I am finding cheese, spicy beef and food in the gears of the drive box'
    )


def generate_existing_work_order_list() -> WorkOrderListModel:
    return WorkOrderListModel(
        work_orders=[
            # WorkOrderModel(
            #     id=456,
            #     equipment='equipment_1',
            #     description='there is a taco stuck in the machine'
            # ),
            WorkOrderModel(
                id=22,
                equipment='equipment_1',
                description='the machine has caught fire'
            ),
            WorkOrderModel(
                id=989,
                equipment='equipment_1',
                description='Every time I eat my lunch over the machine it stops running'
            ),
            WorkOrderModel(
                id=778,
                equipment='equipment_1',
                description='The machine seems to have run out of grease and is making lots of noise'
            ),
            # WorkOrderModel(
            #     id=1266,
            #     equipment='equipment_1',
            #     description='When I start this equipment it smells like chili powder and spices'
            # )
        ]
    )