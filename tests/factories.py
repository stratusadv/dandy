from tests.schemas.work_order_schemas import WorkOrderSchema, ExistingWorkOrderListSchema


def generate_current_work_order_schema_data() -> WorkOrderSchema:
    return WorkOrderSchema(
        id=1234,
        equipment='equipment_1',
        description='I am finding cheese and spicy beef in the gears'
    )


def generate_existing_work_order_list_schema_data() -> ExistingWorkOrderListSchema:
    return ExistingWorkOrderListSchema(
        work_orders=[
            WorkOrderSchema(
                id=456,
                equipment='equipment_1',
                description='there is a taco stuck in the machine'
            ),
            WorkOrderSchema(
                id=22,
                equipment='equipment_1',
                description='the machine has caught fire'
            ),
            WorkOrderSchema(
                id=989,
                equipment='equipment_1',
                description='Every time I eat my lunch by the machine it stops running'
            )
        ]
    )