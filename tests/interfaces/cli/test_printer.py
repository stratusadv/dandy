import threading
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Callable
from unittest import TestCase, mock

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.application.agent.session import session
from dandy.interfaces.cli.tui.printer import (
    Printer,
    _StoryProgress,
    agents_md_banner_line,
    format_verbose_duration,
    linkify_file_paths,
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

        self.assertIn('Reading the test file.', frame)
        self.assertNotIn('•', frame)
        self.assertNotIn('took', frame)

    def test_current_frame_renders_description_only_beat_plain(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        frame = progress.frame(StoryBeat(description='Checking the forecast now.'), '...')

        self.assertIn('Checking the forecast now.', frame)
        self.assertNotIn('•', frame)
        self.assertNotIn(progress.term.bold_grey, frame)
        self.assertIn(f'{progress.term.bold_orange}Evaluating ...{progress.term.normal}', frame)

    def test_animating_frame_renders_bold_orange_evaluating_suffix(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(description='Checking the forecast now.')

        animating_frame = progress.frame(beat, '..')
        settled_frame = progress.settled_frame(beat)

        self.assertIn(f'{progress.term.bold_orange}Evaluating ..{progress.term.normal}', animating_frame)
        self.assertNotIn('Evaluating', settled_frame)

    def test_frames_style_label_grey_and_description_plain(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(label='Reading', description='src/foo.py lines 1-10')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        self.assertTrue(animating_frame.startswith(f'\r{term.normal}{term.bold_grey}Reading'))
        self.assertIn(f'{term.bold_grey}Reading{term.normal}', animating_frame)
        self.assertIn('src/foo.py', animating_frame)
        self.assertIn('lines 1-10', animating_frame)

        self.assertTrue(settled_frame.startswith(f'\r{term.normal}• '))
        self.assertNotIn('Reading', settled_frame)
        self.assertNotIn(term.bold_grey, settled_frame)
        self.assertIn('src/foo.py', settled_frame)
        self.assertIn('lines 1-10', settled_frame)

    def test_frames_style_mutating_label_orange(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(label='Writing', description='src/foo.py', can_mutate_state=True)

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        self.assertIn(f'{term.bold_orange}Writing{term.normal}', animating_frame)
        self.assertNotIn(term.bold_grey, animating_frame)
        self.assertIn('src/foo.py', animating_frame)

        self.assertNotIn('Writing', settled_frame)
        self.assertNotIn(term.bold_grey, settled_frame)
        self.assertIn('src/foo.py', settled_frame)

    def test_narration_beat_renders_bold_blue(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(description='Let me check the weather.', kind='narration')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        for frame in (animating_frame, settled_frame):
            self.assertNotIn('•', frame)
            self.assertIn(term.bold_blue, frame)
            self.assertIn('Let me check the weather.', frame)
            self.assertNotIn(term.bold_grey, frame)

    def test_tool_beat_renders_its_own_ascii_char(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(label='Reading', description='src/foo.py', ascii_char='>')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        self.assertIn(f'{term.normal}> ', animating_frame)
        self.assertTrue(settled_frame.startswith(f'\r{term.normal}> '))

    def test_multiline_beat_animates_on_a_single_line(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        description = 'pytest -q\nimport blessed\nprint(1)'
        beat = StoryBeat(label='Executing', description=description, ascii_char='>')

        animating_frame = progress.frame(beat, '...')
        next_frame = progress.frame(beat, '....')
        settled_frame = progress.settled_frame(beat)

        self.assertEqual(animating_frame.count('\n'), 1)
        animated_line = animating_frame.split('\n', 1)[1]
        self.assertTrue(animated_line.startswith(f'{term.normal}> '))
        self.assertIn('pytest -q import blessed print(1)', animating_frame)
        self.assertNotIn('\n', next_frame)
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


class TestStoryProgressHeadingGrouping(TestCase):
    def setUp(self) -> None:
        self.progress = _StoryProgress(Terminal(force_styling='default'))

    def test_first_labeled_beat_gets_a_heading(self) -> None:
        beat = StoryBeat(label='Reading', description='src/a.py')
        self.progress.update(beat)

        frame = self.progress.frame(beat, '.')

        self.assertIn('Reading', frame)
        self.assertIn('src/a.py', frame)

    def test_repeated_label_shares_the_first_heading(self) -> None:
        first = StoryBeat(label='Reading', description='src/a.py')
        second = StoryBeat(label='Reading', description='src/b.py')
        self.progress.update(first)
        self.progress.update(second)

        first_frame = self.progress.frame(first, '.')
        first_settled = self.progress.settled_frame(first)
        second_frame = self.progress.frame(second, '.')
        second_settled = self.progress.settled_frame(second)

        self.assertIn('Reading', first_frame)
        self.assertNotIn('Reading', first_settled)
        self.assertNotIn('Reading', second_frame)
        self.assertNotIn('Reading', second_settled)
        self.assertIn('src/a.py', first_settled)
        self.assertIn('src/b.py', second_frame)

    def test_heading_prints_once_across_animating_and_settling(self) -> None:
        beat = StoryBeat(label='Reading', description='src/a.py')

        first_frame = self.progress.frame(beat, '.')
        second_frame = self.progress.frame(beat, '..')
        settled = self.progress.settled_frame(beat)

        self.assertIn('Reading', first_frame)
        self.assertNotIn('Reading', second_frame)
        self.assertNotIn('Reading', settled)

    def test_label_change_emits_a_new_heading(self) -> None:
        reading = StoryBeat(label='Reading', description='src/a.py')
        writing = StoryBeat(label='Writing', description='src/b.py')
        self.progress.update(reading)
        self.progress.update(writing)

        reading_frame = self.progress.frame(reading, '.')
        reading_settled = self.progress.settled_frame(reading)
        writing_frame = self.progress.frame(writing, '.')

        self.assertIn('Reading', reading_frame)
        self.assertNotIn('Reading', reading_settled)
        self.assertIn('Writing', writing_frame)
        self.assertNotIn('Reading', writing_frame)
        self.assertIn('src/b.py', writing_frame)

    def test_reappearing_label_gets_a_fresh_heading(self) -> None:
        reading = StoryBeat(label='Reading', description='src/a.py')
        writing = StoryBeat(label='Writing', description='src/b.py')
        reading_again = StoryBeat(label='Reading', description='src/c.py')
        self.progress.update(reading)
        self.progress.update(writing)
        self.progress.update(reading_again)

        self.progress.frame(reading, '.')
        self.progress.settled_frame(reading)
        self.progress.frame(writing, '.')
        self.progress.settled_frame(writing)
        reading_again_frame = self.progress.frame(reading_again, '.')

        self.assertIn('Reading', reading_again_frame)
        self.assertIn('src/c.py', reading_again_frame)

    def test_non_tool_beat_does_not_break_the_group(self) -> None:
        first = StoryBeat(label='Reading', description='src/a.py')
        narration = StoryBeat(description='Let me check the other file.', kind='narration')
        second = StoryBeat(label='Reading', description='src/b.py')
        self.progress.update(first)
        self.progress.update(narration)
        self.progress.update(second)

        first_settled = self.progress.settled_frame(first)
        narration_settled = self.progress.settled_frame(narration)
        second_frame = self.progress.frame(second, '.')

        self.assertIn('Reading', first_settled)
        self.assertNotIn('Reading', narration_settled)
        self.assertNotIn('Reading', second_frame)
        self.assertNotIn('•', narration_settled)

    def test_settled_frame_emits_heading_when_beat_never_animated(self) -> None:
        first = StoryBeat(label='Reading', description='src/a.py')
        second = StoryBeat(label='Reading', description='src/b.py')
        self.progress.update(first)
        self.progress.update(second)

        first_settled = self.progress.settled_frame(first)
        second_settled = self.progress.settled_frame(second)

        self.assertIn('Reading', first_settled)
        self.assertNotIn('Reading', second_settled)
        self.assertIn('src/a.py', first_settled)
        self.assertIn('src/b.py', second_settled)


class TestLinkifyFilePaths(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.project_base_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.project_base_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def test_relative_path_with_slash_is_linked(self) -> None:
        expected_uri = (self.project_base_path / 'src' / 'foo.py').as_uri()

        linked = linkify_file_paths('Reading src/foo.py lines 1-10')

        self.assertEqual(
            linked,
            f'Reading \x1b]8;;{expected_uri}\x1b\\src/foo.py\x1b]8;;\x1b\\ lines 1-10',
        )

    def test_extension_only_word_is_linked(self) -> None:
        expected_uri = (self.project_base_path / 'foo.py').as_uri()

        linked = linkify_file_paths('Editing foo.py everywhere')

        self.assertIn(f'\x1b]8;;{expected_uri}\x1b\\foo.py\x1b]8;;\x1b\\', linked)
        self.assertIn('everywhere', linked)

    def test_non_path_words_are_untouched(self) -> None:
        text = 'Running pytest -q lines 1-10 1.0.5 v2.0 end . recursively'

        self.assertEqual(linkify_file_paths(text), text)

    def test_absolute_path_links_its_own_uri(self) -> None:
        expected_uri = Path('/etc/hosts').as_uri()

        linked = linkify_file_paths('Editing /etc/hosts')

        self.assertIn(f'\x1b]8;;{expected_uri}\x1b\\/etc/hosts\x1b]8;;\x1b\\', linked)

    def test_frames_link_file_paths_in_tool_beats(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(label='Reading', description='src/foo.py lines 1-10')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        expected_uri = (self.project_base_path / 'src' / 'foo.py').as_uri()

        for frame in (animating_frame, settled_frame):
            self.assertIn(f'\x1b]8;;{expected_uri}\x1b\\src/foo.py\x1b]8;;\x1b\\', frame)
            self.assertIn('lines 1-10', frame)

    def test_description_only_beats_are_not_linked(self) -> None:
        progress = _StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(description='Checking src/foo.py now.', kind='narration')

        animating_frame = progress.frame(beat, '...')
        settled_frame = progress.settled_frame(beat)

        for frame in (animating_frame, settled_frame):
            self.assertNotIn('\x1b]8', frame)


class TestPrinterEditedFiles(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.project_base_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.project_base_path
        self.printer = Printer(Terminal(force_styling='default'))

        self.print_patch = mock.patch('builtins.print')
        self.mock_print = self.print_patch.start()
        self.addCleanup(self.print_patch.stop)

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def test_empty_list_prints_nothing(self) -> None:
        self.printer.edited_files([])

        self.mock_print.assert_not_called()

    def test_paths_print_as_bulleted_links_under_a_heading(self) -> None:
        expected_foo_uri = (self.project_base_path / 'src' / 'foo.py').as_uri()
        expected_bar_uri = (self.project_base_path / 'src' / 'bar.py').as_uri()

        self.printer.edited_files(['src/foo.py', 'src/bar.py'])

        lines = [call.args[0] for call in self.mock_print.call_args_list]

        self.assertEqual(len(lines), 3)
        self.assertIn('Edited files:', lines[0])
        self.assertIn(self.printer.term.bold_grey, lines[0])
        self.assertTrue(lines[1].startswith(f'{self.printer.term.normal}• '))
        self.assertIn(f'\x1b]8;;{expected_foo_uri}\x1b\\src/foo.py\x1b]8;;\x1b\\', lines[1])
        self.assertTrue(lines[2].startswith(f'{self.printer.term.normal}• '))
        self.assertIn(f'\x1b]8;;{expected_bar_uri}\x1b\\src/bar.py\x1b]8;;\x1b\\', lines[2])
