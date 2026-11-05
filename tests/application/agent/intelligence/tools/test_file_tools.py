from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from dandy.application.agent.intelligence.tools import (
    CODE_EDITING_TOOLS,
    CreateDirectoryTool,
    DeleteFileTool,
    EditFileTool,
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)
from dandy.application.agent.session import session


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

    def test_can_mutate_state_flags_mutating_tools(self) -> None:
        self.assertTrue(WriteFileTool().can_mutate_state)
        self.assertTrue(EditFileTool().can_mutate_state)
        self.assertTrue(DeleteFileTool().can_mutate_state)
        self.assertTrue(CreateDirectoryTool().can_mutate_state)
        self.assertFalse(ReadFileTool().can_mutate_state)
        self.assertFalse(ListDirectoryTool().can_mutate_state)

    def test_write_file_creates_parent_directories(self):
        result = WriteFileTool().handle(file_path='nested/dir/example.txt', content='hello world')

        self.assertTrue(result.startswith('Successfully wrote'))
        self.assertTrue(Path(self.temp_directory_path, 'nested', 'dir', 'example.txt').is_file())

    def test_read_file_with_line_numbers(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('first line\nsecond line\nthird line\n')

        result = ReadFileTool().handle(file_path='example.txt')

        self.assertIn('1 | first line', result)
        self.assertIn('2 | second line', result)
        self.assertIn('3 | third line', result)

    def test_read_file_line_range(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('1\n2\n3\n4\n5\n')

        result = ReadFileTool().handle(file_path='example.txt', start_line=2, end_line=4)

        self.assertIn('2 | 2', result)
        self.assertIn('4 | 4', result)
        self.assertNotIn('1 | 1', result)
        self.assertNotIn('5 | 5', result)

    def test_read_file_missing_returns_error(self):
        result = ReadFileTool().handle(file_path='missing.txt')

        self.assertIn('does not exist', result)

    def test_read_file_caps_long_output(self) -> None:
        target_path = Path(self.temp_directory_path, 'big.txt')
        target_path.write_text('\n'.join(f'line number {i} with padding' for i in range(1, 3001)))

        result = ReadFileTool().handle(file_path='big.txt')

        self.assertLess(len(result), 8200)
        self.assertIn('1 | line number 1 with padding', result)
        self.assertIn('... (truncated', result)
        self.assertIn('3000 lines', result)
        self.assertIn('start_line and end_line', result)
        self.assertNotIn('3000 |', result)

    def test_read_file_short_output_is_not_capped(self) -> None:
        target_path = Path(self.temp_directory_path, 'small.txt')
        target_path.write_text('one\ntwo\nthree\n')

        result = ReadFileTool().handle(file_path='small.txt')

        self.assertNotIn('truncated', result)
        self.assertIn('3 | three', result)

    def test_edit_file_single_replacement(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo bar baz')

        result = EditFileTool().handle(file_path='example.txt', old_string='foo', new_string='qux')

        self.assertIn('1 replacement', result)
        self.assertIn('line 1', result)
        self.assertIn('"foo"', result)
        self.assertEqual(target_path.read_text(), 'qux bar baz')

    def test_edit_file_multiline_replacement_reports_line_range(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('alpha\none two\nthree\nomega\n')

        result = EditFileTool().handle(
            file_path='example.txt', old_string='one two\nthree', new_string='replaced'
        )

        self.assertIn('1 replacement', result)
        self.assertIn('lines 2-3', result)
        self.assertIn('"one two"', result)
        self.assertEqual(target_path.read_text(), 'alpha\nreplaced\nomega\n')

    def test_distinct_edits_to_one_file_return_distinct_results(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('alpha\nbeta\ngamma\n')

        first = EditFileTool().handle(file_path='example.txt', old_string='alpha', new_string='one')
        second = EditFileTool().handle(file_path='example.txt', old_string='gamma', new_string='three')

        self.assertNotEqual(first, second)

    def test_repeated_noop_edit_returns_identical_result(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo bar')

        first = EditFileTool().handle(file_path='example.txt', old_string='foo', new_string='foo')
        second = EditFileTool().handle(file_path='example.txt', old_string='foo', new_string='foo')

        self.assertEqual(first, second)

    def test_edit_file_not_found_returns_error(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo bar')

        result = EditFileTool().handle(
            file_path='example.txt', old_string='missing', new_string='baz'
        )

        self.assertIn('was not found', result)
        self.assertEqual(target_path.read_text(), 'foo bar')

    def test_edit_file_ambiguous_without_replace_all_returns_error(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo foo foo')

        result = EditFileTool().handle(file_path='example.txt', old_string='foo', new_string='bar')

        self.assertIn('found 3 times', result)
        self.assertEqual(target_path.read_text(), 'foo foo foo')

    def test_edit_file_replace_all(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('foo foo foo')

        result = EditFileTool().handle(
            file_path='example.txt', old_string='foo', new_string='bar', replace_all=True
        )

        self.assertIn('3 replacement', result)
        self.assertIn('line 1', result)
        self.assertIn('"foo"', result)
        self.assertEqual(target_path.read_text(), 'bar bar bar')

    def test_delete_file(self):
        target_path = Path(self.temp_directory_path, 'example.txt')
        target_path.write_text('delete me')

        result = DeleteFileTool().handle(file_path='example.txt')

        self.assertIn('Deleted', result)
        self.assertFalse(target_path.exists())

    def test_create_directory(self):
        result = CreateDirectoryTool().handle(directory_path='nested/dir')

        self.assertIn('Created', result)
        self.assertTrue(Path(self.temp_directory_path, 'nested', 'dir').is_dir())

    def test_list_directory(self):
        Path(self.temp_directory_path, 'first.txt').write_text('a')
        Path(self.temp_directory_path, 'nested').mkdir()
        Path(self.temp_directory_path, 'nested', 'second.txt').write_text('b')

        result = ListDirectoryTool().handle(path='', recursive=True)

        self.assertIn('first.txt', result)
        self.assertIn('nested/second.txt', result)

    def test_list_directory_caps_long_output(self) -> None:
        for index in range(300):
            Path(self.temp_directory_path, f'file_number_{index:04d}_with_padding.txt').write_text(
                'x'
            )

        result = ListDirectoryTool().handle(path='')

        self.assertLess(len(result), 8200)
        self.assertIn('... (truncated)', result)

    def test_path_traversal_is_blocked(self):
        result = WriteFileTool().handle(file_path='../outside.txt', content='should not be written')

        self.assertIn('outside the project', result)
        self.assertFalse(Path(self.temp_directory_path.parent, 'outside.txt').exists())

    def test_file_tools_provide_action_labels_and_outputs(self):
        labels = [
            ReadFileTool().action_label,
            WriteFileTool().action_label,
            EditFileTool().action_label,
            DeleteFileTool().action_label,
            CreateDirectoryTool().action_label,
            ListDirectoryTool().action_label,
        ]

        for label in labels:
            self.assertIsInstance(label, str)
            self.assertTrue(label)

        self.assertEqual(ReadFileTool().action_label, 'Reading')
        self.assertEqual(ReadFileTool().action_output(file_path='a.txt'), 'a.txt')
        self.assertEqual(
            ReadFileTool().action_output(file_path='a.txt', start_line=5, end_line=10),
            'a.txt lines 5-10',
        )
        self.assertEqual(WriteFileTool().action_label, 'Writing')
        self.assertEqual(WriteFileTool().action_output(file_path='b.txt'), 'b.txt')
        self.assertEqual(EditFileTool().action_label, 'Editing')
        self.assertEqual(
            EditFileTool().action_output(file_path='c.txt', replace_all=True), 'c.txt everywhere'
        )
        self.assertEqual(DeleteFileTool().action_label, 'Deleting')
        self.assertEqual(DeleteFileTool().action_output(file_path='d.txt'), 'd.txt')
        self.assertEqual(CreateDirectoryTool().action_label, 'Creating directory')
        self.assertEqual(CreateDirectoryTool().action_output(directory_path='e'), 'e')
        self.assertEqual(ListDirectoryTool().action_label, 'Listing')
        self.assertEqual(
            ListDirectoryTool().action_output(path='f', recursive=True), 'f recursively'
        )
