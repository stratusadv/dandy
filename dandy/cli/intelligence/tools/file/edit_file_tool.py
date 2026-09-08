from dandy.cli.intelligence.tools.paths import _resolve_project_path
from dandy.file.utils import read_from_file, write_to_file
from dandy.tool.tool import BaseTool


class EditFileTool(BaseTool):
    name = 'edit_file'
    description = (
        'Apply a targeted text replacement inside an existing file. '
        'The path is relative to the project root. '
        'Provide the exact old_string (including whitespace) that exists in the file. '
        'Set replace_all to True to replace every occurrence instead of just one.'
    )

    def handle(
        self, file_path: str, old_string: str, new_string: str, replace_all: bool = False
    ) -> str:
        try:
            resolved_file_path = _resolve_project_path(file_path)

            if not resolved_file_path.is_file():
                return f'Error: file "{file_path}" does not exist.'

            content = read_from_file(resolved_file_path)

            occurrence_count = content.count(old_string)

            if occurrence_count == 0:
                return (
                    f'Error: the text to replace was not found in "{file_path}". '
                    f'The file has {len(content.splitlines())} line(s); '
                    f'provide the exact text including whitespace.'
                )

            if occurrence_count > 1 and not replace_all:
                return (
                    f'Error: the text to replace was found {occurrence_count} times '
                    f'in "{file_path}". Provide more surrounding context '
                    f'or set replace_all to True.'
                )

            write_to_file(resolved_file_path, content.replace(old_string, new_string))
        except Exception as error:
            return f'Error editing file: {error}'

        return f'Applied {occurrence_count} replacement(s) to "{file_path}".'
