from dandy.application.agent.intelligence.tools.clock import CLOCK_TOOLS, ClockTool
from dandy.application.agent.intelligence.tools.command import COMMAND_TOOLS, RunCommandTool
from dandy.application.agent.intelligence.tools.file import (
    CODE_EDITING_TOOLS,
    SEARCH_TOOLS,
    CreateDirectoryTool,
    DeleteFileTool,
    EditFileTool,
    ListDirectoryTool,
    ReadFileTool,
    SearchFilesTool,
    WriteFileTool,
)
from dandy.application.agent.intelligence.tools.git import GIT_TOOLS, GitDiffTool, GitStatusTool
from dandy.application.agent.intelligence.tools.question import (
    QUESTION_TOOLS,
    QuestionHandler,
    QuestionTool,
)
from dandy.domain.tool.tool import ToolType

AGENT_TOOLS: list[ToolType] = [
    *CODE_EDITING_TOOLS,
    *SEARCH_TOOLS,
    *COMMAND_TOOLS,
    *GIT_TOOLS,
    *CLOCK_TOOLS,
]

__all__ = [
    'AGENT_TOOLS',
    'CLOCK_TOOLS',
    'CODE_EDITING_TOOLS',
    'COMMAND_TOOLS',
    'GIT_TOOLS',
    'QUESTION_TOOLS',
    'SEARCH_TOOLS',
    'ClockTool',
    'CreateDirectoryTool',
    'DeleteFileTool',
    'EditFileTool',
    'GitDiffTool',
    'GitStatusTool',
    'ListDirectoryTool',
    'QuestionHandler',
    'QuestionTool',
    'ReadFileTool',
    'RunCommandTool',
    'SearchFilesTool',
    'WriteFileTool',
]
