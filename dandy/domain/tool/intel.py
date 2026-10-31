from pydantic import Field

from dandy.domain.intel.intel import BaseIntel, BaseListIntel


class ToolCallIntel(BaseIntel):
    name: str
    arguments: str = ''
    id: str | None = None


class ToolCallsIntel(BaseListIntel[ToolCallIntel]):
    calls: list[ToolCallIntel] = Field(default_factory=list)
    summary: str = ''
