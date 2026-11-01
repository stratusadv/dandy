import threading
from time import sleep
from typing import Callable
from unittest import TestCase, mock

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.interfaces.cli.tui.printer import Printer, _StoryProgress, format_verbose_duration
from dandy.shared.cancellation import StopSignal
from dandy.shared.exceptions import RunStoppedError


class TestFormatVerboseDuration(TestCase):
    def test_seconds_under_a_minute(self) -> None:
        self.assertEqual(format_verbose_duration(2.0), '2.0 seconds')

    def test_minutes_and_seconds(self) -> None:
        self.assertEqual(format_verbose_duration(125), '2 minutes and 5 seconds')

    def test_single_minute(self) -> None:
        self.assertEqual(format_verbose_duration(60), '1 minute')

    def test_hours_minutes_and_seconds(self) -> None:
        self.assertEqual(format_verbose_duration(3661), '1 hour and 1 minute and 1 second')


class TestPrinterStory(TestCase):
    def setUp(self) -> None:
        self.printer = Printer(Terminal())

        self.stdout_patch = mock.patch('sys.stdout.write')
        self.mock_write = self.stdout_patch.start()
        self.addCleanup(self.stdout_patch.stop)

        self.print_patch = mock.patch('builtins.print')
        self.mock_print = self.print_patch.start()
        self.addCleanup(self.print_patch.stop)

    def test_settled_frame_is_plain_text_without_duration(self) -> None:
        progress = _StoryProgress(Terminal(), step_indent=2)
        frame = progress.settled_frame('Reading the test file.')

        self.assertIn('Reading the test file.', frame)
        self.assertNotIn('took', frame)

    def test_current_frame_renders_beat_in_blue(self) -> None:
        progress = _StoryProgress(Terminal(), step_indent=2)
        frame = progress.frame('Checking the forecast now.', '...')

        self.assertIn('Checking the forecast now.', frame)
        self.assertIn(progress.term.bold_blue, frame)

    def test_run_timed_task_prints_story_and_completion_sentence(self) -> None:
        release = threading.Event()

        def work(update: Callable[[str], None]) -> object:
            update('Reading the test file to understand it.')
            sleep(0.05)
            update('Running the tests to verify my change.')
            release.wait()
            return {'text': 'done'}

        threading.Timer(0.15, release.set).start()

        result = self.printer.run_timed_task(action_name='Coding', task='fix bug', work=work)

        self.assertEqual(result, {'text': 'done'})

        written = [str(call.args[0]) for call in self.mock_write.call_args_list if call.args]
        story_lines = [line for line in written if '↳ ' in line and line.endswith('\n')]

        self.assertTrue(
            any('Reading the test file to understand it.' in line for line in story_lines)
        )
        self.assertTrue(
            any('Running the tests to verify my change.' in line for line in story_lines)
        )

        printed_lines = [str(call.args[0]) for call in self.mock_print.call_args_list if call.args]
        completion_lines = [
            line for line in printed_lines if 'I have completed your request in ' in line
        ]

        self.assertEqual(len(completion_lines), 1)
        self.assertTrue(completion_lines[0].endswith('.'))

    def test_run_timed_task_propagates_stop_error_from_work(self) -> None:
        def work(update: Callable[[str], None]) -> object:
            raise RunStoppedError('Run stopped by user.')

        with self.assertRaises(RunStoppedError):
            self.printer.run_timed_task(
                action_name='Coding', task='stop me', work=work, stop_signal=StopSignal()
            )

    @mock.patch.object(Terminal, 'inkey')
    def test_run_timed_task_double_escape_sets_stop_signal(
        self, mock_inkey: mock.MagicMock
    ) -> None:
        stop_signal = StopSignal()
        release = threading.Event()

        def work(update: Callable[[str], None]) -> object:
            release.wait(5)
            return 'done'

        escape = Keystroke('\x1b')
        mock_inkey.side_effect = [escape, escape]

        threading.Timer(0.3, release.set).start()

        result = self.printer.run_timed_task(
            action_name='Coding', task='stop me', work=work, stop_signal=stop_signal
        )

        self.assertEqual(result, 'done')
        self.assertTrue(stop_signal.is_set())

        printed_lines = [str(call.args[0]) for call in self.mock_print.call_args_list if call.args]
        self.assertTrue(any('Stopping...' in line for line in printed_lines))

    @mock.patch.object(Terminal, 'inkey')
    def test_run_timed_task_combined_double_escape_sets_stop_signal(
        self, mock_inkey: mock.MagicMock
    ) -> None:
        stop_signal = StopSignal()
        release = threading.Event()

        def work(update: Callable[[str], None]) -> object:
            release.wait(5)
            return 'done'

        # blessed may deliver two quick escapes as one keystroke.
        mock_inkey.side_effect = [Keystroke('\x1b\x1b')]

        threading.Timer(0.3, release.set).start()

        result = self.printer.run_timed_task(
            action_name='Coding', task='stop me', work=work, stop_signal=stop_signal
        )

        self.assertEqual(result, 'done')
        self.assertTrue(stop_signal.is_set())

    @mock.patch.object(Terminal, 'inkey')
    def test_run_timed_task_single_escape_does_not_stop(self, mock_inkey: mock.MagicMock) -> None:
        stop_signal = StopSignal()
        release = threading.Event()

        def work(update: Callable[[str], None]) -> object:
            release.wait(5)
            return 'done'

        mock_inkey.side_effect = [Keystroke('\x1b'), Keystroke('a')]

        threading.Timer(0.3, release.set).start()

        result = self.printer.run_timed_task(
            action_name='Coding', task='keep going', work=work, stop_signal=stop_signal
        )

        self.assertEqual(result, 'done')
        self.assertFalse(stop_signal.is_set())

    @mock.patch.object(Terminal, 'inkey')
    def test_run_timed_task_without_stop_signal_never_polls_keys(
        self, mock_inkey: mock.MagicMock
    ) -> None:
        release = threading.Event()

        def work(update: Callable[[str], None]) -> object:
            release.wait(5)
            return 'done'

        threading.Timer(0.15, release.set).start()

        result = self.printer.run_timed_task(action_name='Coding', task='no stop', work=work)

        self.assertEqual(result, 'done')
        mock_inkey.assert_not_called()

    @mock.patch.object(Terminal, 'inkey', side_effect=OSError('no tty'))
    def test_run_timed_task_survives_unreadable_stdin(self, mock_inkey: mock.MagicMock) -> None:
        release = threading.Event()

        def work(update: Callable[[str], None]) -> object:
            release.wait(5)
            return 'done'

        threading.Timer(0.15, release.set).start()

        result = self.printer.run_timed_task(
            action_name='Coding', task='no tty', work=work, stop_signal=StopSignal()
        )

        self.assertEqual(result, 'done')
