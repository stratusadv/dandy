from typing import Any

from dandy.application.agent.tools.paths import resolve_project_path
from dandy.application.agent.tools.tool_errors import tool_error
from dandy.shared.files import make_directory
from dandy.domain.tool.tool import BaseTool


class CreateDirectoryTool(BaseTool):
    name = 'create_directory'
    description = (
        'Create a directory, including any missing parent directories. '
        'The path is relative to the project root.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        return f'Creating directory {kwargs["directory_path"]}.'

    @tool_error('creating directory')
    def handle(self, directory_path: str) -> str:
        resolved_directory_path = resolve_project_path(directory_path)

        make_directory(resolved_directory_path)

        return f'Created directory "{directory_path}".'
