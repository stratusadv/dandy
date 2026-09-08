from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from dandy.cli.intelligence.tools.command.command_tool import RunCommandTool
from dandy.cli.intelligence.tools.git.git_diff_tool import GitDiffTool
from dandy.cli.intelligence.tools.git.git_status_tool import GitStatusTool
from dandy.cli.intelligence.tools.file.search_tool import SearchFilesTool
from dandy.cli.session import session


class TestSearchFilesTool(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def test_search_plain_text_is_case_insensitive(self) -> None:
        Path(self.temp_directory_path, 'alpha.py').write_text('def hello_world():\n    pass\n')
        Path(self.temp_directory_path, 'nested').mkdir()
        Path(self.temp_directory_path, 'nested', 'beta.txt').write_text(
            'nothing here\nHELLO WORLD up here\n'
        )

        result = SearchFilesTool().handle(query='hello')

        self.assertIn('alpha.py:1: def hello_world():', result)
        self.assertIn('nested/beta.txt:2: HELLO WORLD up here', result)

    def test_search_with_regex(self) -> None:
        Path(self.temp_directory_path, 'sample.py').write_text(
            'value_1 = 1\nvalue_12 = 2\nother = 3\n'
        )

        result = SearchFilesTool().handle(query=r'value_\d+', use_regex=True)

        self.assertIn('sample.py:1: value_1 = 1', result)
        self.assertIn('sample.py:2: value_12 = 2', result)
        self.assertNotIn('other', result)

    def test_search_excludes_hidden_and_dependency_directories(self) -> None:
        Path(self.temp_directory_path, '.git').mkdir()
        Path(self.temp_directory_path, '.git', 'config').write_text('needle secret\n')
        Path(self.temp_directory_path, 'node_modules').mkdir()
        Path(self.temp_directory_path, 'node_modules', 'dep.js').write_text('needle here\n')
        Path(self.temp_directory_path, '.venv').mkdir()
        Path(self.temp_directory_path, '.venv', 'package.py').write_text('needle too\n')
        Path(self.temp_directory_path, 'real.py').write_text('needle match\n')

        result = SearchFilesTool().handle(query='needle')

        self.assertIn('real.py:1: needle match', result)
        self.assertNotIn('.git', result)
        self.assertNotIn('node_modules', result)
        self.assertNotIn('.venv', result)

    def test_search_no_matches(self) -> None:
        result = SearchFilesTool().handle(query='does not exist')

        self.assertIn('No matches found', result)

    def test_search_invalid_regex_returns_error(self) -> None:
        result = SearchFilesTool().handle(query='(', use_regex=True)

        self.assertIn('invalid regex', result)

    def test_search_path_must_be_a_directory(self) -> None:
        Path(self.temp_directory_path, 'file.txt').write_text('needle\n')

        result = SearchFilesTool().handle(query='needle', path='file.txt')

        self.assertIn('is not a directory', result)

    def test_search_outside_project_is_blocked(self) -> None:
        result = SearchFilesTool().handle(query='needle', path='../outside')

        self.assertIn('outside the project', result)


class TestRunCommandTool(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    @mock.patch('dandy.cli.intelligence.tools.command.command_tool.run_subprocess')
    def test_run_command_executes_subprocess(self, mock_run_subprocess: mock.MagicMock) -> None:
        mock_run_subprocess.return_value = 'Exit code: 0\ncommand output'

        result = RunCommandTool().handle(command='ls -la')

        self.assertEqual(result, 'Exit code: 0\ncommand output')
        mock_run_subprocess.assert_called_once_with(
            command='ls -la', cwd=session.project_base_path, timeout_seconds=30, use_shell=True
        )


class TestGitTools(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    @mock.patch('dandy.cli.intelligence.tools.git.git_status_tool.run_subprocess')
    def test_git_status_runs_short_status(self, mock_run_subprocess: mock.MagicMock) -> None:
        mock_run_subprocess.return_value = ' M file.py'

        result = GitStatusTool().handle()

        self.assertEqual(result, ' M file.py')
        mock_run_subprocess.assert_called_once_with(
            command=['git', 'status', '--short'],
            cwd=session.project_base_path,
            timeout_seconds=10,
            use_shell=False,
        )

    @mock.patch('dandy.cli.intelligence.tools.git.git_diff_tool.run_subprocess')
    def test_git_diff_whole_repository(self, mock_run_subprocess: mock.MagicMock) -> None:
        mock_run_subprocess.return_value = 'diff output'

        result = GitDiffTool().handle()

        self.assertEqual(result, 'diff output')
        mock_run_subprocess.assert_called_once_with(
            command=['git', 'diff'],
            cwd=session.project_base_path,
            timeout_seconds=10,
            use_shell=False,
        )

    @mock.patch('dandy.cli.intelligence.tools.git.git_diff_tool.run_subprocess')
    def test_git_diff_with_path(self, mock_run_subprocess: mock.MagicMock) -> None:
        Path(self.temp_directory_path, 'file.py').write_text('x = 1\n')

        GitDiffTool().handle(path='file.py')

        mock_run_subprocess.assert_called_once_with(
            command=['git', 'diff', '--', 'file.py'],
            cwd=session.project_base_path,
            timeout_seconds=10,
            use_shell=False,
        )

    def test_git_diff_outside_project_is_blocked(self) -> None:
        result = GitDiffTool().handle(path='../outside')

        self.assertIn('Error running git diff', result)
        self.assertIn('outside the project', result)
