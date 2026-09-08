from typing import Any

from dandy.cli.intelligence.tools.paths import _resolve_project_path
from dandy.file.utils import make_directory
from dandy.tool.tool import BaseTool


class CreateDirectoryTool(BaseTool):
    name = 'create_directory'
    description = (
        'Create a directory, including any missing parent directories. '
        'The path is relative to the project root.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        return f'Creating directory {kwargs["directory_path"]}.'

    def handle(self, directory_path: str) -> str:
        try:
            resolved_directory_path = _resolve_project_path(directory_path)

            make_directory(resolved_directory_path)
        except Exception as error:
            return f'Error creating directory: {error}'

        return f'Created directory "{directory_path}".'
