from pydantic import Field

from dandy.intel.intel import BaseIntel, BaseListIntel


class LlmToolCallIntel(BaseIntel):
    name: str
    arguments: str = ''
    id: str | None = None


class LlmToolCallsIntel(BaseListIntel[LlmToolCallIntel]):
    calls: list[LlmToolCallIntel] = Field(default_factory=list)
