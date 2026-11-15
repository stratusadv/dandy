from dandy.application.agent.intelligence.tools.clock.clock_tool import ClockTool
from dandy.domain.tool.tool import ToolType

CLOCK_TOOLS: list[ToolType] = [ClockTool]

__all__ = ['CLOCK_TOOLS', 'ClockTool']
