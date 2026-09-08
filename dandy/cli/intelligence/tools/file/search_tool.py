import re
from pathlib import Path
from typing import Any

from dandy.cli.intelligence.tools.paths import _resolve_project_path, _to_relative_path
from dandy.tool.tool import BaseTool

_EXCLUDED_DIRECTORIES = {'.git', '.dandy', 'node_modules', '.venv', '__pycache__'}

_MAX_FILE_SIZE_BYTES = 1_000_000

_MAX_LINE_CHARACTERS = 300

_SEARCH_RESULT_CHARACTER_LIMIT = 8000


class SearchFilesTool(BaseTool):
    name = 'search_files'
    description = (
        'Search text inside files for a query and return matching lines with their '
        'file paths and line numbers. The path is relative to the project root '
        '(empty means the project root). By default the query is a plain, '
        'case-insensitive text search; set use_regex to True to treat the query '
        'as a regular expression (also case-insensitive). Hidden directories, '
        'dependency folders, and binary or very large files are skipped.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        query = kwargs['query']
        path = kwargs.get('path') or ''

        if path:
            return f'Searching for "{query}" in {path}.'

        return f'Searching for "{query}".'

    def handle(self, query: str, path: str = '', use_regex: bool = False) -> str:
        try:
            search_path = _resolve_project_path(path)

            if not search_path.is_dir():
                return f'Error: "{path or "."}" is not a directory.'

            matches = self._search_files(search_path, query, use_regex)
        except Exception as error:
            return f'Error searching files: {error}'

        if not matches:
            return f'No matches found for "{query}".'

        output = '\n'.join(matches)

        if len(output) > _SEARCH_RESULT_CHARACTER_LIMIT:
            output = output[:_SEARCH_RESULT_CHARACTER_LIMIT] + '\n... (truncated)'

        return output

    def _search_files(self, search_path: Path, query: str, use_regex: bool) -> list[str]:
        regex = None

        if use_regex:
            try:
                regex = re.compile(query, re.IGNORECASE)
            except re.error as error:
                error_message = f'invalid regex: {error}'
                raise ValueError(error_message) from error

        search_query = query.lower()

        matches = []

        for file_path in search_path.rglob('*'):
            if file_path.is_dir() or self._should_skip(file_path):
                continue

            try:
                lines = file_path.read_text(encoding='utf-8', errors='ignore').splitlines()
            except OSError:
                continue

            for line_number, line in enumerate(lines, start=1):
                if regex is not None:
                    if not regex.search(line):
                        continue
                elif search_query not in line.lower():
                    continue

                relative_path = _to_relative_path(file_path)

                if len(line) > _MAX_LINE_CHARACTERS:
                    line = line[:_MAX_LINE_CHARACTERS] + '...'

                matches.append(f'{relative_path}:{line_number}: {line}')

        return matches

    @staticmethod
    def _should_skip(file_path: Path) -> bool:
        if any(part in _EXCLUDED_DIRECTORIES for part in file_path.parts):
            return True

        try:
            if file_path.stat().st_size > _MAX_FILE_SIZE_BYTES:
                return True
        except OSError:
            return True

        return False
