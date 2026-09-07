from pathlib import Path

from dandy.cli.tools.intel import (
    CreateDirectoryIntel,
    DeleteFileIntel,
    EditFileIntel,
    ListDirectoryIntel,
    ReadFileIntel,
    WriteFileIntel,
)
from dandy.cli.tools.paths import _resolve_project_path, _to_relative_path
from dandy.file.utils import (
    get_directory_listing,
    make_directory,
    read_from_file,
    remove_file,
    write_to_file,
)
from dandy.tool.tool import BaseTool, ToolType


class ListDirectoryTool(BaseTool):
    name = 'list_directory'
    description = (
        'List the files and directories inside a directory. '
        'The path is relative to the project root (empty means the project root). '
        'Set recursive to True to include nested directories.'
    )
    intel_class = ListDirectoryIntel

    def handle(self, arguments: ListDirectoryIntel) -> str:
        try:
            directory_path = _resolve_project_path(arguments.path)

            if not directory_path.is_dir():
                return f'Error: "{arguments.path or "."}" is not a directory.'

            items = get_directory_listing(
                directory_path,
                max_depth=None if arguments.recursive else 1,
            )

            relative_items = [
                _to_relative_path(Path(item))
                for item in items
            ]
        except Exception as error:
            return f'Error listing directory: {error}'

        if not relative_items:
            return f'The directory "{arguments.path or "."}" is empty.'

        return '\n'.join(relative_items)


class ReadFileTool(BaseTool):
    name = 'read_file'
    description = (
        'Read the contents of a file with line numbers. '
        'The path is relative to the project root. '
        'Optionally provide start_line and end_line (1-based, inclusive) '
        'to read only part of the file.'
    )
    intel_class = ReadFileIntel

    def handle(self, arguments: ReadFileIntel) -> str:
        try:
            file_path = _resolve_project_path(arguments.file_path)

            if not file_path.is_file():
                return f'Error: file "{arguments.file_path}" does not exist.'

            lines = read_from_file(file_path).splitlines()

            start_line = arguments.start_line or 1
            end_line = arguments.end_line or len(lines)

            start_line = max(1, start_line)
            end_line = min(len(lines), end_line)

            if start_line > end_line:
                return (
                    f'Error: start_line {start_line} is after end_line {end_line}. '
                    f'The file has {len(lines)} lines.'
                )

            numbered_lines = [
                f'{line_number:>6} | {line}'
                for line_number, line in enumerate(
                    lines[start_line - 1:end_line],
                    start=start_line,
                )
            ]
        except Exception as error:
            return f'Error reading file: {error}'

        return '\n'.join(numbered_lines)


class WriteFileTool(BaseTool):
    name = 'write_file'
    description = (
        'Write content to a file, creating the file and any missing parent directories, '
        'or overwriting an existing file entirely. The path is relative to the project root.'
    )
    intel_class = WriteFileIntel

    def handle(self, arguments: WriteFileIntel) -> str:
        try:
            file_path = _resolve_project_path(arguments.file_path)

            write_to_file(file_path, arguments.content)

            line_count = len(arguments.content.splitlines())
        except Exception as error:
            return f'Error writing file: {error}'

        return f'Successfully wrote {line_count} line(s) to "{arguments.file_path}".'


class EditFileTool(BaseTool):
    name = 'edit_file'
    description = (
        'Apply a targeted text replacement inside an existing file. '
        'The path is relative to the project root. '
        'Provide the exact old_string (including whitespace) that exists in the file. '
        'Set replace_all to True to replace every occurrence instead of just one.'
    )
    intel_class = EditFileIntel

    def handle(self, arguments: EditFileIntel) -> str:
        try:
            file_path = _resolve_project_path(arguments.file_path)

            if not file_path.is_file():
                return f'Error: file "{arguments.file_path}" does not exist.'

            content = read_from_file(file_path)

            occurrence_count = content.count(arguments.old_string)

            if occurrence_count == 0:
                return (
                    f'Error: the text to replace was not found in "{arguments.file_path}". '
                    f'The file has {len(content.splitlines())} line(s); '
                    f'provide the exact text including whitespace.'
                )

            if occurrence_count > 1 and not arguments.replace_all:
                return (
                    f'Error: the text to replace was found {occurrence_count} times '
                    f'in "{arguments.file_path}". Provide more surrounding context '
                    f'or set replace_all to True.'
                )

            write_to_file(
                file_path,
                content.replace(arguments.old_string, arguments.new_string),
            )
        except Exception as error:
            return f'Error editing file: {error}'

        return f'Applied {occurrence_count} replacement(s) to "{arguments.file_path}".'


class DeleteFileTool(BaseTool):
    name = 'delete_file'
    description = 'Delete a file. The path is relative to the project root.'
    intel_class = DeleteFileIntel

    def handle(self, arguments: DeleteFileIntel) -> str:
        try:
            file_path = _resolve_project_path(arguments.file_path)

            if not file_path.is_file():
                return f'Error: file "{arguments.file_path}" does not exist.'

            remove_file(file_path)
        except Exception as error:
            return f'Error deleting file: {error}'

        return f'Deleted file "{arguments.file_path}".'


class CreateDirectoryTool(BaseTool):
    name = 'create_directory'
    description = (
        'Create a directory, including any missing parent directories. '
        'The path is relative to the project root.'
    )
    intel_class = CreateDirectoryIntel

    def handle(self, arguments: CreateDirectoryIntel) -> str:
        try:
            directory_path = _resolve_project_path(arguments.directory_path)

            make_directory(directory_path)
        except Exception as error:
            return f'Error creating directory: {error}'

        return f'Created directory "{arguments.directory_path}".'


CODE_EDITING_TOOLS: list[ToolType] = [
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    DeleteFileTool,
    CreateDirectoryTool,
]
