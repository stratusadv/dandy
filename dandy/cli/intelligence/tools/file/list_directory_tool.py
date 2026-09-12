from pathlib import Path
from typing import Any

from dandy.cli.intelligence.tools.paths import resolve_project_path, to_relative_path
from dandy.cli.intelligence.tools.tool_errors import tool_error
from dandy.file.utils import get_directory_listing
from dandy.tool.tool import BaseTool


class ListDirectoryTool(BaseTool):
    name = 'list_directory'
    description = (
        'List the files and directories inside a directory. '
        'The path is relative to the project root (empty means the project root). '
        'Set recursive to True to include nested directories.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        path = kwargs.get('path') or '.'
        recursive = kwargs.get('recursive', False)

        return f'Listing {path}{" recursively" if recursive else ""}.'

    @tool_error('listing directory')
    def handle(self, path: str = '', recursive: bool = False) -> str:
        directory_path = resolve_project_path(path)

        if not directory_path.is_dir():
            return f'Error: "{path or "."}" is not a directory.'

        items = get_directory_listing(directory_path, max_depth=None if recursive else 1)

        relative_items = [to_relative_path(Path(item)) for item in items]

        if not relative_items:
            return f'The directory "{path or "."}" is empty.'

        return '\n'.join(relative_items)
