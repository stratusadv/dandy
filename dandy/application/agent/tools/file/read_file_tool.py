from typing import Any

from dandy.application.agent.tools.paths import resolve_project_path
from dandy.application.agent.tools.tool_errors import tool_error
from dandy.shared.files import read_from_file
from dandy.domain.tool.tool import BaseTool

_READ_FILE_CHARACTER_LIMIT = 8000


class ReadFileTool(BaseTool):
    name = 'read_file'
    description = (
        'Read the contents of a file with line numbers. '
        'The path is relative to the project root. '
        'Optionally provide start_line and end_line (1-based, inclusive) '
        'to read only part of the file. '
        'Long files are returned truncated; page through them with start_line and end_line.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        file_path = kwargs['file_path']
        start_line = kwargs.get('start_line')
        end_line = kwargs.get('end_line')

        if start_line or end_line:
            return f'Reading {file_path} lines {start_line or 1}-{end_line or "end"}.'

        return f'Reading {file_path}.'

    @tool_error('reading file')
    def handle(
        self, file_path: str, start_line: int | None = None, end_line: int | None = None
    ) -> str:
        resolved_file_path = resolve_project_path(file_path)

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
            for line_number, line in enumerate(lines[first_line - 1 : last_line], start=first_line)
        ]

        numbered_output = '\n'.join(numbered_lines)

        if len(numbered_output) > _READ_FILE_CHARACTER_LIMIT:
            kept_output = numbered_output[:_READ_FILE_CHARACTER_LIMIT]
            newline_position = kept_output.rfind('\n')

            if newline_position > 0:
                kept_output = kept_output[:newline_position]

            return (
                kept_output + f'\n... (truncated; the file has {len(lines)} lines, '
                'use start_line and end_line to read more)'
            )

        return numbered_output
