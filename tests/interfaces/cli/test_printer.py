import threading
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Callable
from unittest import TestCase, mock

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.interfaces.cli.tui.printer import (
    Printer,
    _StoryProgress,
    agents_md_banner_line,
    format_verbose_duration,
)
from dandy.domain.tool.beat import StoryBeat
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


class TestAgentsMdBannerLine(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.project_base_path = Path(self.temp_directory_context.name)

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_banner_line_when_the_file_is_missing(self) -> None:
        self.assertEqual(
            agents_md_banner_line(self.project_base_path), 'not found - run /init to create one'
        )

    def test_banner_line_with_a_small_file(self) -> None:
        (self.project_base_path / 'AGENTS.md').write_text('small', encoding='utf-8')

        self.assertEqual(
            agents_md_banner_line(self.project_base_path),
            'found (5 bytes) - loaded into the agent system prompt',
        )

    def test_banner_line_with_a_large_file(self) -> None:
        (self.project_base_path / 'AGENTS.md').write_text('x' * 2048, encoding='utf-8')

        self.assertEqual(
            agents_md_banner_line(self.project_base_path),
            'found (2.0 KB) - loaded into the agent system prompt',
        )


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
        progress = _StoryProgress(Terminal())
        frame = progress.settled_frame(StoryBeat(description='Reading the test file.'))

        self.assertIn('• Reading the test file.', frame)
        self.assertIn('Reading the test file.', frame)
        self.assertNotIn('took', frame)

    def test_current_frame_renders_description_only_beat_plain(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        frame = progress.frame(StoryBeat(description='Checking the forecast now.'), '...')

        self.assertIn('• Checking the forecast now.', frame)
        self.assertIn('Checking the forecast now.', frame)
        self.assertNotIn(progress.term.bold_blue, frame)
        self.assertNotIn(progress.term.bold_grey, frame)

    def test_frames_style_label_grey_and_description_plain(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(label='Reading', description='src/foo.py lines 1-10')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        for frame in (animating_frame, settled_frame):
            self.assertTrue(frame.startswith(f'\r{progress.term.normal}• '))
            self.assertIn(progress.term.bold_grey, frame)
            self.assertIn('Reading', frame)
            self.assertIn('src/foo.py lines 1-10', frame)

    def test_narration_beat_renders_bold_blue(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(description='Let me check the weather.', kind='narration')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        for frame in (animating_frame, settled_frame):
            self.assertTrue(frame.startswith(f'\r{progress.term.normal}• '))
            self.assertIn(progress.term.bold_blue, frame)
            self.assertIn('Let me check the weather.', frame)
            self.assertNotIn(progress.term.bold_grey, frame)

    def test_tool_beat_renders_its_own_ascii_char(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(label='Reading', description='src/foo.py', ascii_char='>')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        for frame in (animating_frame, settled_frame):
            self.assertTrue(frame.startswith(f'\r{progress.term.normal}> '))

    def test_multiline_beat_animates_on_a_single_line(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        description = 'pytest -q\nimport blessed\nprint(1)'
        beat = StoryBeat(label='Executing', description=description, ascii_char='>')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        self.assertNotIn('\n', animating_frame)
        self.assertTrue(animating_frame.startswith(f'\r{progress.term.normal}> '))
        self.assertIn('pytest -q import blessed print(1)', animating_frame)
        self.assertIn(description, settled_frame)

    def test_event_prints_text_without_prefix(self) -> None:
        self.printer.event('Hello')

        self.assertEqual(self.mock_print.call_args_list[0].args[0], 'Hello')

        self.printer.event('Hi', end='')

        self.assertEqual(self.mock_print.call_args_list[1].kwargs['end'], '')

    def test_run_timed_task_prints_story_and_completion_sentence(self) -> None:
        release = threading.Event()

        def work(update: Callable[[StoryBeat], None]) -> object:
            update(StoryBeat(description='Reading the test file to understand it.'))
            sleep(0.05)
            update(StoryBeat(label='Running', description='"pytest -q"'))
            release.wait()
            return {'text': 'done'}

        threading.Timer(0.15, release.set).start()

        result = self.printer.run_timed_task(action_name='Coding', task='fix bug', work=work)

        self.assertEqual(result, {'text': 'done'})

        written = [str(call.args[0]) for call in self.mock_write.call_args_list if call.args]
        story_lines = [line for line in written if line.endswith('\n')]

        self.assertTrue(
            any('Reading the test file to understand it.' in line for line in story_lines)
        )
        self.assertTrue(any('"pytest -q"' in line for line in story_lines))

        printed_lines = [str(call.args[0]) for call in self.mock_print.call_args_list if call.args]
        completion_lines = [
            line for line in printed_lines if 'I have completed your request in ' in line
        ]

        self.assertEqual(len(completion_lines), 1)
        self.assertTrue(completion_lines[0].endswith('.'))

    def test_run_timed_task_propagates_stop_error_from_work(self) -> None:
        def work(update: Callable[[StoryBeat], None]) -> object:
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

        def work(update: Callable[[StoryBeat], None]) -> object:
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

        def work(update: Callable[[StoryBeat], None]) -> object:
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

        def work(update: Callable[[StoryBeat], None]) -> object:
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

        def work(update: Callable[[StoryBeat], None]) -> object:
            release.wait(5)
            return 'done'

        threading.Timer(0.15, release.set).start()

        result = self.printer.run_timed_task(action_name='Coding', task='no stop', work=work)

        self.assertEqual(result, 'done')
        mock_inkey.assert_not_called()

    @mock.patch.object(Terminal, 'inkey', side_effect=OSError('no tty'))
    def test_run_timed_task_survives_unreadable_stdin(self, mock_inkey: mock.MagicMock) -> None:
        release = threading.Event()

        def work(update: Callable[[StoryBeat], None]) -> object:
            release.wait(5)
            return 'done'

        threading.Timer(0.15, release.set).start()

        result = self.printer.run_timed_task(
            action_name='Coding', task='no tty', work=work, stop_signal=StopSignal()
        )

        self.assertEqual(result, 'done')
