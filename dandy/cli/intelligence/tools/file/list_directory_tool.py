from pathlib import Path

from dandy.cli.intelligence.tools.paths import _resolve_project_path, _to_relative_path
from dandy.file.utils import get_directory_listing
from dandy.tool.tool import BaseTool


class ListDirectoryTool(BaseTool):
    name = 'list_directory'
    description = (
        'List the files and directories inside a directory. '
        'The path is relative to the project root (empty means the project root). '
        'Set recursive to True to include nested directories.'
    )

    def handle(self, path: str = '', recursive: bool = False) -> str:
        try:
            directory_path = _resolve_project_path(path)

            if not directory_path.is_dir():
                return f'Error: "{path or "."}" is not a directory.'

            items = get_directory_listing(directory_path, max_depth=None if recursive else 1)

            relative_items = [_to_relative_path(Path(item)) for item in items]
        except Exception as error:
            return f'Error listing directory: {error}'

        if not relative_items:
            return f'The directory "{path or "."}" is empty.'

        return '\n'.join(relative_items)
