from typing import Any

from dandy.cli.intelligence.tools.paths import _resolve_project_path
from dandy.file.utils import read_from_file
from dandy.tool.tool import BaseTool


class ReadFileTool(BaseTool):
    name = 'read_file'
    description = (
        'Read the contents of a file with line numbers. '
        'The path is relative to the project root. '
        'Optionally provide start_line and end_line (1-based, inclusive) '
        'to read only part of the file.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        file_path = kwargs['file_path']
        start_line = kwargs.get('start_line')
        end_line = kwargs.get('end_line')

        if start_line or end_line:
            return f'Reading {file_path} lines {start_line or 1}-{end_line or "end"}.'

        return f'Reading {file_path}.'

    def handle(
        self, file_path: str, start_line: int | None = None, end_line: int | None = None
    ) -> str:
        try:
            resolved_file_path = _resolve_project_path(file_path)

            if not resolved_file_path.is_file():
                return f'Error: file "{file_path}" does not exist.'

            lines = read_from_file(resolved_file_path).splitlines()

            first_line = start_line or 1
            last_line = end_line or len(lines)

            first_line = max(1, first_line)
            last_line = min(len(lines), last_line)

            if first_line > last_line:
                return (
                    f'Error: start_line {first_line} is after end_line {last_line}. '
                    f'The file has {len(lines)} lines.'
                )

            numbered_lines = [
                f'{line_number:>6} | {line}'
                for line_number, line in enumerate(
                    lines[first_line - 1 : last_line], start=first_line
                )
            ]
        except Exception as error:
            return f'Error reading file: {error}'

        return '\n'.join(numbered_lines)
