from pydantic import Field

from dandy.domain.intel.intel import BaseIntel, BaseListIntel


class LlmToolCallIntel(BaseIntel):
    name: str
    arguments: str = ''
    id: str | None = None


class LlmToolCallsIntel(BaseListIntel[LlmToolCallIntel]):
    calls: list[LlmToolCallIntel] = Field(default_factory=list)
    summary: str = ''
