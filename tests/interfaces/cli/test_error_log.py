from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from dandy.application.agent.session import session
from dandy.interfaces.cli.cli import DandyCli
from dandy.interfaces.cli.error_log import ERROR_LOG_MAX_LINES, error_log_path, log_cli_error
from dandy.interfaces.cli.tui.tui import tui


def _raise_and_log(project_base_path: Path, context: str) -> Path | None:
    def raise_error() -> None:
        message = 'boom'

        raise ValueError(message)

    try:
        raise_error()
    except ValueError as error:
        return log_cli_error(project_base_path, context, error)


class TestErrorLogPath(TestCase):
    def test_error_log_path_lives_under_the_project_dandy_directory(self) -> None:
        project_base_path = Path('project')

        self.assertEqual(error_log_path(project_base_path), Path('project/.dandy/logs/errors.log'))


class TestLogCliError(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.project_base_path = Path(self.temp_directory_context.name)

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_logs_context_exception_and_traceback(self) -> None:
        log_path = _raise_and_log(self.project_base_path, 'agent turn')

        self.assertEqual(log_path, error_log_path(self.project_base_path))

        lines = log_path.read_text(encoding='utf-8').splitlines()

        self.assertTrue(any('agent turn' in line for line in lines))
        self.assertIn('ValueError: boom', lines)
        self.assertIn('Traceback (most recent call last):', lines)
        self.assertTrue(any('_raise_and_log' in line for line in lines))

    def test_new_errors_are_appended_after_existing_entries(self) -> None:
        _raise_and_log(self.project_base_path, 'first context')

        _raise_and_log(self.project_base_path, 'second context')

        lines = error_log_path(self.project_base_path).read_text(encoding='utf-8').splitlines()

        self.assertEqual(lines.count('ValueError: boom'), 2)
        self.assertLess(
            next(index for index, line in enumerate(lines) if 'first context' in line),
            next(index for index, line in enumerate(lines) if 'second context' in line),
        )

    def test_trims_to_the_max_lines_keeping_the_newest(self) -> None:
        log_path = error_log_path(self.project_base_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, 'w', encoding='utf-8') as log_file:
            seeded_lines = (f'old line {index}' for index in range(ERROR_LOG_MAX_LINES + 5))
            log_file.write('\n'.join(seeded_lines) + '\n')

        _raise_and_log(self.project_base_path, 'agent turn')

        lines = log_path.read_text(encoding='utf-8').splitlines()

        self.assertEqual(len(lines), ERROR_LOG_MAX_LINES)
        self.assertIn('ValueError: boom', lines)
        self.assertIn(f'old line {ERROR_LOG_MAX_LINES + 4}', lines)
        self.assertNotIn('old line 0', lines)

    def test_write_failure_returns_none_without_raising(self) -> None:
        blocker_path = Path(self.project_base_path, '.dandy', 'logs')
        blocker_path.parent.mkdir(parents=True, exist_ok=True)
        blocker_path.write_text('a file, not a directory', encoding='utf-8')

        log_path = _raise_and_log(self.project_base_path, 'agent turn')

        self.assertIsNone(log_path)


class TestCliErrorLogIntegration(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

        with mock.patch.object(tui.printer, 'welcome'):
            self.cli = DandyCli()

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    @mock.patch(
        'dandy.application.agent.cli.cli_agent.CliAgent.turn', side_effect=RuntimeError('turn boom')
    )
    @mock.patch.object(tui.printer, 'error')
    def test_failed_agent_turn_writes_to_the_error_log(
        self, _mock_error: mock.MagicMock, _mock_turn: mock.MagicMock
    ) -> None:
        self.cli.process_user_input('do something')

        log_path = error_log_path(self.temp_directory_path)

        self.assertTrue(log_path.is_file())
        content = log_path.read_text(encoding='utf-8')

        self.assertIn('agent turn', content)
        self.assertIn('RuntimeError: turn boom', content)

    @mock.patch(
        'dandy.application.agent.cli.cli_agent.CliAgent.run_init_pass',
        side_effect=RuntimeError('init boom'),
    )
    @mock.patch.object(tui.printer, 'error')
    def test_failed_init_pass_writes_to_the_error_log(
        self, _mock_error: mock.MagicMock, _mock_run_init_pass: mock.MagicMock
    ) -> None:
        self.cli.run_init()

        log_path = error_log_path(self.temp_directory_path)

        self.assertTrue(log_path.is_file())
        content = log_path.read_text(encoding='utf-8')

        self.assertIn('init', content)
        self.assertIn('RuntimeError: init boom', content)
