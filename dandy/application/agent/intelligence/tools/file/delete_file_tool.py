from typing import Any

from dandy.application.agent.intelligence.tools.paths import resolve_project_path
from dandy.application.agent.intelligence.tools.tool_errors import tool_error
from dandy.shared.files import remove_file
from dandy.domain.tool.tool import BaseTool


class DeleteFileTool(BaseTool):
    name = 'delete_file'
    description = 'Delete a file. The path is relative to the project root.'

    action_label = 'Deleting'
    can_mutate_state = True

    def action_output(self, **kwargs: Any) -> str:
        return kwargs['file_path']

    @tool_error('deleting file')
    def handle(self, file_path: str) -> str:
        resolved_file_path = resolve_project_path(file_path)

        if not resolved_file_path.is_file():
            return f'Error: file "{file_path}" does not exist.'

        remove_file(resolved_file_path)

        return f'Deleted file "{file_path}".'
