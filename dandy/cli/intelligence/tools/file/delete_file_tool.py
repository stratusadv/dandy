from dandy.cli.intelligence.tools.paths import _resolve_project_path
from dandy.file.utils import remove_file
from dandy.tool.tool import BaseTool


class DeleteFileTool(BaseTool):
    name = 'delete_file'
    description = 'Delete a file. The path is relative to the project root.'

    def handle(self, file_path: str) -> str:
        try:
            resolved_file_path = _resolve_project_path(file_path)

            if not resolved_file_path.is_file():
                return f'Error: file "{file_path}" does not exist.'

            remove_file(resolved_file_path)
        except Exception as error:
            return f'Error deleting file: {error}'

        return f'Deleted file "{file_path}".'
