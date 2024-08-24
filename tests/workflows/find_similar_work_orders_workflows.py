from dandy.workflow.step import Step
from dandy.workflow.workflow import Workflow

class FindSimilarWorkOrdersWorkflow(Workflow):
    steps = [
        Step(
            name='Get Other Work Orders',
            handler=None,
            output_schema=None,
        ),
        Step(
            name='Compare Current Work Orders to Other Work Orders',
            handler=None,
            output_schema=None,
        ),
        Step(
            name='Return Other Work Orders Schema Data',
            handler=None,
            output_schema=None,
        )
    ]


