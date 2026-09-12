from typing import Any

from dandy.cli.intelligence.tools.paths import resolve_project_path
from dandy.cli.intelligence.tools.tool_errors import tool_error
from dandy.file.utils import write_to_file
from dandy.tool.tool import BaseTool


class WriteFileTool(BaseTool):
    name = 'write_file'
    description = (
        'Write content to a file, creating the file and any missing parent directories, '
        'or overwriting an existing file entirely. The path is relative to the project root.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        return f'Writing {kwargs["file_path"]}.'

    @tool_error('writing file')
    def handle(self, file_path: str, content: str) -> str:
        resolved_file_path = resolve_project_path(file_path)

        write_to_file(resolved_file_path, content)

        line_count = len(content.splitlines())

        return f'Successfully wrote {line_count} line(s) to "{file_path}".'
