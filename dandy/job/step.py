from dandy.job.enums import StepStatus


class Step:
    def __init__(
            self,
            description: str,
            status: StepStatus = StepStatus.NOT_STARTED
    ):
        self.description = description
        self.status = status
