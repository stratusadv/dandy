import threading
from time import sleep
from typing import Callable
from unittest import TestCase, mock

from blessed import Terminal

from dandy.cli.tui.printer import Printer, _StoryProgress, format_verbose_duration


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
            sleep(0.2)
            update('Running the tests to verify my change.')
            release.wait()
            return {'text': 'done'}

        threading.Timer(0.6, release.set).start()

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
