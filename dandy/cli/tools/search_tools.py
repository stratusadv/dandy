import re
from pathlib import Path

from dandy.cli.tools.intel import SearchFilesIntel
from dandy.cli.tools.paths import _resolve_project_path, _to_relative_path
from dandy.tool.tool import BaseTool

_EXCLUDED_DIRECTORIES = {
    '.git',
    '.dandy',
    'node_modules',
    '.venv',
    '__pycache__',
}

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
    intel_class = SearchFilesIntel

    def handle(self, arguments: SearchFilesIntel) -> str:
        try:
            search_path = _resolve_project_path(arguments.path)

            if not search_path.is_dir():
                return f'Error: "{arguments.path or "."}" is not a directory.'

            matches = self._search_files(search_path, arguments)
        except Exception as error:
            return f'Error searching files: {error}'

        if not matches:
            return f'No matches found for "{arguments.query}".'

        output = '\n'.join(matches)

        if len(output) > _SEARCH_RESULT_CHARACTER_LIMIT:
            output = output[:_SEARCH_RESULT_CHARACTER_LIMIT] + '\n... (truncated)'

        return output

    def _search_files(self, search_path: Path, arguments: SearchFilesIntel) -> list[str]:
        regex = None

        if arguments.use_regex:
            try:
                regex = re.compile(arguments.query, re.IGNORECASE)
            except re.error as error:
                error_message = f'invalid regex: {error}'
                raise ValueError(error_message) from error

        search_query = arguments.query.lower()

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
