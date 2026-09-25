from typing import Any

from dandy.application.agent.tools.paths import resolve_project_path
from dandy.application.agent.tools.tool_errors import tool_error
from dandy.shared.files import remove_file
from dandy.domain.tool.tool import BaseTool


class DeleteFileTool(BaseTool):
    name = 'delete_file'
    description = 'Delete a file. The path is relative to the project root.'

    def action_sentence(self, **kwargs: Any) -> str:
        return f'Deleting {kwargs["file_path"]}.'

    @tool_error('deleting file')
    def handle(self, file_path: str) -> str:
        resolved_file_path = resolve_project_path(file_path)

        if not resolved_file_path.is_file():
            return f'Error: file "{file_path}" does not exist.'

        remove_file(resolved_file_path)

        return f'Deleted file "{file_path}".'
