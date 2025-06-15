from abc import ABC

from dandy.core.processor.processor import BaseProcessor
from dandy.conf import settings


class BaseAgent(BaseProcessor, ABC):
    plan_time_limit_seconds: int = settings.DEFAULT_AGENT_PLAN_TIME_LIMIT_SECONDS
    plan_task_count_limit: int = settings.DEFAULT_AGENT_PLAN_TASK_COUNT_LIMIT
