class EventActorType:
    AGENT = 'agent'
    DEPARTMENT = 'department',
    LLM = 'llm'
    JOB = 'job'
    TASK = 'task'
    WORKFLOW = 'workflow'


class StepStatus:
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'
    ERROR = 'error'