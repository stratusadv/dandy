from dandy.cli.intelligence.tools.paths import _resolve_project_path
from dandy.file.utils import write_to_file
from dandy.tool.tool import BaseTool


class WriteFileTool(BaseTool):
    name = 'write_file'
    description = (
        'Write content to a file, creating the file and any missing parent directories, '
        'or overwriting an existing file entirely. The path is relative to the project root.'
    )

    def handle(self, file_path: str, content: str) -> str:
        try:
            resolved_file_path = _resolve_project_path(file_path)

            write_to_file(resolved_file_path, content)

            line_count = len(content.splitlines())
        except Exception as error:
            return f'Error writing file: {error}'

        return f'Successfully wrote {line_count} line(s) to "{file_path}".'
