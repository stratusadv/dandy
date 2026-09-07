from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from dandy.cli.actions.code.tools import (
    CODE_EDITING_TOOLS,
    CreateDirectoryTool,
    DeleteFileTool,
    EditFileTool,
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)
from dandy.cli.actions.code.tools.intel import (
    CreateDirectoryIntel,
    DeleteFileIntel,
    EditFileIntel,
    ListDirectoryIntel,
    ReadFileIntel,
    WriteFileIntel,
)
from dandy.cli.session import session


class TestCodeEditingTools(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def test_code_editing_tools_listing(self):
        self.assertEqual(len(CODE_EDITING_TOOLS), 6)

        tool_names = {tool().name for tool in CODE_EDITING_TOOLS}

        self.assertEqual(
            tool_names,
            {
                'list_directory',
                'read_file',
                'write_file',
                'edit_file',
                'delete_file',
                'create_directory',
            },
        )

    def test_write_file_creates_parent_directories(self):
        result = WriteFileTool().handle(
            WriteFileIntel(
                file_path='nested/dir/example.txt',
                content='hello world',
            )
        )

        self.assertTrue(result.startswith('Successfully wrote'))
        self.assertTrue(Path(self.temp_directory_path, 'nested', 'dir', 'example.txt').is_file())

    def test_read_file_with_line_numbers(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('first line\nsecond line\nthird line\n')

        result = ReadFileTool().handle(
            ReadFileIntel(file_path='example.txt')
        )

        self.assertIn('1 | first line', result)
        self.assertIn('2 | second line', result)
        self.assertIn('3 | third line', result)

    def test_read_file_line_range(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('1\n2\n3\n4\n5\n')

        result = ReadFileTool().handle(
            ReadFileIntel(file_path='example.txt', start_line=2, end_line=4)
        )

        self.assertIn('2 | 2', result)
        self.assertIn('4 | 4', result)
        self.assertNotIn('1 | 1', result)
        self.assertNotIn('5 | 5', result)

    def test_read_file_missing_returns_error(self):
        result = ReadFileTool().handle(
            ReadFileIntel(file_path='missing.txt')
        )

        self.assertIn('does not exist', result)

    def test_edit_file_single_replacement(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo bar baz')

        result = EditFileTool().handle(
            EditFileIntel(
                file_path='example.txt',
                old_string='foo',
                new_string='qux',
            )
        )

        self.assertIn('1 replacement', result)
        self.assertEqual(target_path.read_text(), 'qux bar baz')

    def test_edit_file_not_found_returns_error(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo bar')

        result = EditFileTool().handle(
            EditFileIntel(
                file_path='example.txt',
                old_string='missing',
                new_string='baz',
            )
        )

        self.assertIn('was not found', result)
        self.assertEqual(target_path.read_text(), 'foo bar')

    def test_edit_file_ambiguous_without_replace_all_returns_error(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo foo foo')

        result = EditFileTool().handle(
            EditFileIntel(
                file_path='example.txt',
                old_string='foo',
                new_string='bar',
            )
        )

        self.assertIn('found 3 times', result)
        self.assertEqual(target_path.read_text(), 'foo foo foo')

    def test_edit_file_replace_all(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo foo foo')

        result = EditFileTool().handle(
            EditFileIntel(
                file_path='example.txt',
                old_string='foo',
                new_string='bar',
                replace_all=True,
            )
        )

        self.assertIn('3 replacement', result)
        self.assertEqual(target_path.read_text(), 'bar bar bar')

    def test_delete_file(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('delete me')

        result = DeleteFileTool().handle(
            DeleteFileIntel(file_path='example.txt')
        )

        self.assertIn('Deleted', result)
        self.assertFalse(target_path.exists())

    def test_create_directory(self):
        result = CreateDirectoryTool().handle(
            CreateDirectoryIntel(directory_path='nested/dir')
        )

        self.assertIn('Created', result)
        self.assertTrue(Path(self.temp_directory_path, 'nested', 'dir').is_dir())

    def test_list_directory(self):
        Path(self.temp_directory_path, 'first.txt').write_text('a')
        Path(self.temp_directory_path, 'nested').mkdir()
        Path(self.temp_directory_path, 'nested', 'second.txt').write_text('b')

        result = ListDirectoryTool().handle(
            ListDirectoryIntel(path='', recursive=True)
        )

        self.assertIn('first.txt', result)
        self.assertIn('nested/second.txt', result)

    def test_path_traversal_is_blocked(self):
        result = WriteFileTool().handle(
            WriteFileIntel(
                file_path='../outside.txt',
                content='should not be written',
            )
        )

        self.assertIn('outside the project', result)
        self.assertFalse(Path(self.temp_directory_path.parent, 'outside.txt').exists())
