import os
import threading
import types
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Callable
from unittest import TestCase, mock

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.application.agent.session import session
from dandy.interfaces.cli.tui.banner import (
    agents_md_banner_line,
    agents_md_status,
    config_banner_line,
    format_verbose_duration,
    skills_banner_line,
)
from dandy.interfaces.cli.tui.printer import Printer
from dandy.interfaces.cli.tui.story_progress import StoryProgress
from dandy.interfaces.cli.tui.text import linkify_file_paths
from dandy.domain.tool.beat import StoryBeat
from dandy.shared.cancellation import StopSignal
from dandy.shared.exceptions import RunStoppedError
from dandy.shared.interaction import QuestionGate


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

    def test_agents_md_status_found(self) -> None:
        (self.project_base_path / 'AGENTS.md').write_text('small', encoding='utf-8')

        self.assertEqual(agents_md_status(self.project_base_path), 'AGENTS.md Found')

    def test_agents_md_status_missing(self) -> None:
        self.assertEqual(agents_md_status(self.project_base_path), 'AGENTS.md Missing')


class TestConfigBannerLine(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.project_base_path = Path(self.temp_directory_context.name)

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_config_line_shows_config_model_source_and_agents_md_status(self) -> None:
        module = types.ModuleType('fake_settings_module')
        module.__file__ = '/home/user/project/dandy_settings.py'

        with (
            mock.patch(
                'dandy.interfaces.cli.tui.banner.get_cli_llm_config', return_value='DEFAULT'
            ),
            mock.patch(
                'dandy.interfaces.cli.tui.banner.LlmConfig',
                return_value=types.SimpleNamespace(model='stratus.turbo'),
            ),
            mock.patch('dandy.shared.settings.settings.settings._user_settings', new=module),
            mock.patch('dandy.shared.settings.settings.settings._json_settings_path', new=None),
        ):
            line = config_banner_line(self.project_base_path)

        self.assertEqual(
            line,
            'DEFAULT (stratus.turbo) [/home/user/project/dandy_settings.py] · AGENTS.md Missing',
        )

    def test_config_line_uses_the_json_settings_path_when_present(self) -> None:
        (self.project_base_path / 'AGENTS.md').write_text('docs', encoding='utf-8')

        with (
            mock.patch('dandy.interfaces.cli.tui.banner.get_cli_llm_config', return_value='CODING'),
            mock.patch(
                'dandy.interfaces.cli.tui.banner.LlmConfig',
                return_value=types.SimpleNamespace(model='stratus.max'),
            ),
            mock.patch(
                'dandy.shared.settings.settings.settings._user_settings',
                new=types.SimpleNamespace(),
            ),
            mock.patch(
                'dandy.shared.settings.settings.settings._json_settings_path',
                new=self.project_base_path / '.dandy' / 'dandy.json',
            ),
        ):
            line = config_banner_line(self.project_base_path)

        self.assertEqual(
            line,
            f'CODING (stratus.max) [{self.project_base_path / ".dandy" / "dandy.json"}] '
            '· AGENTS.md Found',
        )


class TestSkillsBannerLine(TestCase):
    def test_banner_line_when_no_skills_are_found(self) -> None:
        with mock.patch('dandy.interfaces.cli.tui.banner.load_cli_skills', return_value=([], [])):
            self.assertEqual(
                skills_banner_line(Path('/nonexistent')),
                'none found - drop SKILL.md folders in .dandy/skills/',
            )

    @staticmethod
    def _skill(name: str, active: bool) -> mock.MagicMock:
        skill = mock.MagicMock(active=active)
        skill.name = name
        return skill

    def test_banner_line_counts_active_and_passive_skills(self) -> None:
        skills = [
            self._skill('alpha', True),
            self._skill('bravo', True),
            self._skill('charlie', False),
        ]

        with mock.patch(
            'dandy.interfaces.cli.tui.banner.load_cli_skills', return_value=(skills, [])
        ):
            self.assertEqual(
                skills_banner_line(Path('/nonexistent')),
                '3 loaded (active: alpha, bravo, passive: charlie)',
            )

    def test_banner_line_lists_only_the_first_twenty_skills_per_group(self) -> None:
        skills = [self._skill(f'active-{index}', True) for index in range(25)]
        skills += [self._skill(f'passive-{index}', False) for index in range(3)]

        with mock.patch(
            'dandy.interfaces.cli.tui.banner.load_cli_skills', return_value=(skills, [])
        ):
            line = skills_banner_line(Path('/nonexistent'))

        self.assertTrue(line.startswith('28 loaded (active: '))
        self.assertIn('active-0, active-1, active-2', line)
        self.assertIn('active-19', line)
        self.assertNotIn('active-20', line)
        self.assertIn('active-19...,', line)
        self.assertIn('passive: passive-0, passive-1, passive-2)', line)

    def test_banner_line_full_group_names_when_under_the_limit(self) -> None:
        skills = [self._skill(f'active-{index}', True) for index in range(20)]

        with mock.patch(
            'dandy.interfaces.cli.tui.banner.load_cli_skills', return_value=(skills, [])
        ):
            line = skills_banner_line(Path('/nonexistent'))

        self.assertIn('active-19)', line)
        self.assertNotIn('...', line)

    def test_banner_line_all_passive(self) -> None:
        skills = [self._skill(f'passive-{index}', False) for index in range(3)]

        with mock.patch(
            'dandy.interfaces.cli.tui.banner.load_cli_skills', return_value=(skills, [])
        ):
            line = skills_banner_line(Path('/nonexistent'))

        self.assertEqual(line, '3 loaded (passive: passive-0, passive-1, passive-2)')


class TestPrinterStory(TestCase):
    def setUp(self) -> None:
        env = dict(os.environ)
        env.pop('DANDY_DESKTOP_NOTIFICATIONS', None)
        env.pop('KONSOLE_VERSION', None)

        self.env_patch = mock.patch.dict(os.environ, env, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

        self.printer = Printer(Terminal())

        self.os_notify_patch = mock.patch('dandy.interfaces.cli.tui.notify.os_desktop_notify')
        self.os_notify_patch.start()
        self.addCleanup(self.os_notify_patch.stop)

        self.session_patch = mock.patch(
            'dandy.interfaces.cli.tui.notify.session',
            new=types.SimpleNamespace(project_base_path=Path('/proj')),
        )
        self.session_patch.start()
        self.addCleanup(self.session_patch.stop)

        self.stdout_patch = mock.patch('sys.stdout.write')
        self.mock_write = self.stdout_patch.start()
        self.addCleanup(self.stdout_patch.stop)

        self.print_patch = mock.patch('builtins.print')
        self.mock_print = self.print_patch.start()
        self.addCleanup(self.print_patch.stop)

    def test_settled_frame_is_plain_text_without_duration(self) -> None:
        progress = StoryProgress(Terminal())
        frame = progress.settled_frame(StoryBeat(description='Reading the test file.'))

        self.assertIn('Reading the test file.', frame)
        self.assertNotIn('•', frame)
        self.assertNotIn('took', frame)

    def test_current_frame_renders_description_only_beat_plain(self) -> None:
        with mock.patch(
            'dandy.interfaces.cli.tui.story_progress.thinking_phrase',
            return_value='Polishing a Cufflink',
        ):
            progress = StoryProgress(Terminal(force_styling='default'))
            frame = progress.frame(StoryBeat(description='Checking the forecast now.'))

        lines = frame.split('\n')

        self.assertEqual(len(lines), 2)
        self.assertIn('Checking the forecast now.', lines[0])
        self.assertNotIn('•', frame)
        phrase_line = f'{progress.term.bold_grey}✦ Polishing a Cufflink{progress.term.normal}'
        self.assertIn(phrase_line, lines[1])

    def test_animating_frame_renders_bold_grey_phrase_on_the_next_line(self) -> None:
        with mock.patch(
            'dandy.interfaces.cli.tui.story_progress.thinking_phrase',
            return_value='Polishing a Cufflink',
        ):
            progress = StoryProgress(Terminal(force_styling='default'))
            beat = StoryBeat(description='Checking the forecast now.')

            animating_frame = progress.frame(beat)
            settled_frame = progress.settled_frame(beat)

        lines = animating_frame.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertIn('Checking the forecast now.', lines[0])
        self.assertNotIn('Polishing a Cufflink', lines[0])
        phrase_line = f'{progress.term.bold_grey}✦ Polishing a Cufflink{progress.term.normal}'
        self.assertIn(phrase_line, lines[1])
        self.assertNotIn('Checking the forecast now.', lines[1])
        self.assertNotIn('Polishing a Cufflink', settled_frame)

    def test_animating_frame_holds_the_phrase_for_three_seconds(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(description='Checking the forecast now.')

        with (
            mock.patch(
                'dandy.interfaces.cli.tui.story_progress.thinking_phrase',
                side_effect=['Polishing a Cufflink', 'Dusting a Tailcoat'],
            ) as mock_choice,
            mock.patch(
                'dandy.interfaces.cli.tui.story_progress.perf_counter',
                side_effect=[0.0, 1.5, 2.9, 3.1],
            ),
        ):
            frames = [
                progress.frame(beat),
                progress.frame(beat),
                progress.frame(beat),
                progress.frame(beat),
            ]

        first_phrase = f'{term.bold_grey}✦ Polishing a Cufflink'
        second_phrase = f'{term.bold_grey}✦ Dusting a Tailcoat'

        self.assertIn(first_phrase, frames[0])
        self.assertIn(first_phrase, frames[1])
        self.assertIn(first_phrase, frames[2])
        self.assertNotIn(first_phrase, frames[3])
        self.assertIn(second_phrase, frames[3])
        self.assertEqual(mock_choice.call_count, 2)

    def test_frames_style_label_skyblue_and_description_plain(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(label='Reading', description='src/foo.py lines 1-10')

        animating_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        self.assertTrue(animating_frame.startswith(f'\r{term.normal}\n{term.bold_skyblue}Reading'))
        self.assertIn(f'{term.bold_skyblue}Reading{term.normal}', animating_frame)
        self.assertIn('src/foo.py', animating_frame)
        self.assertIn('lines 1-10', animating_frame)

        self.assertTrue(settled_frame.startswith(f'\x1b[1A\r{term.bold_skyblue}↳{term.normal} '))
        self.assertNotIn('Reading', settled_frame)
        self.assertIn('src/foo.py', settled_frame)
        self.assertIn('lines 1-10', settled_frame)

    def test_frames_style_mutating_label_purple(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(label='Writing', description='src/foo.py', can_mutate_state=True)

        animating_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        self.assertIn(f'{term.bold_purple}Writing{term.normal}', animating_frame)
        self.assertNotIn(term.bold_skyblue, animating_frame)
        self.assertIn('src/foo.py', animating_frame)

        self.assertNotIn('Writing', settled_frame)
        self.assertNotIn(term.bold_skyblue, settled_frame)
        self.assertIn('src/foo.py', settled_frame)

    def test_frames_style_system_affecting_label_orange(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(
            label='Executing',
            description='pytest -q',
            can_mutate_state=True,
            can_affect_system=True,
        )

        animating_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        self.assertIn(f'{term.bold_orange}Executing{term.normal}', animating_frame)
        self.assertNotIn(term.bold_purple, animating_frame)
        self.assertNotIn(term.bold_skyblue, animating_frame)
        self.assertNotIn('Executing', settled_frame)
        self.assertIn('pytest -q', settled_frame)

    def test_frames_style_dangerous_label_red_wins_over_orange_and_purple(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(
            label='Executing',
            description='rm -rf .',
            can_mutate_state=True,
            can_affect_system=True,
            is_dangerous=True,
        )

        animating_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        self.assertIn(f'{term.bold_red}Executing{term.normal}', animating_frame)
        self.assertNotIn(term.bold_orange, animating_frame)
        self.assertNotIn(term.bold_purple, animating_frame)
        self.assertNotIn(term.bold_skyblue, animating_frame)
        self.assertNotIn('Executing', settled_frame)
        self.assertIn('rm -rf .', settled_frame)

    def test_narration_beat_renders_bold_blue(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(description='Let me check the weather.', kind='narration')

        animating_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        for frame in (animating_frame, settled_frame):
            self.assertNotIn('•', frame)
            self.assertIn(term.bold_blue, frame)
            self.assertIn('Let me check the weather.', frame)

        self.assertNotIn(term.bold_grey, settled_frame)

    def test_compaction_beat_renders_bold_purple_after_a_blank_line(self) -> None:
        with mock.patch(
            'dandy.interfaces.cli.tui.story_progress.thinking_phrase',
            return_value='Polishing a Cufflink',
        ):
            progress = StoryProgress(Terminal(force_styling='default'))
            term = progress.term
            beat = StoryBeat(
                description='Compacting my thoughts into a more manageable size', kind='compaction'
            )

            animating_frame = progress.frame(beat)
            settled_frame = progress.settled_frame(beat)

        self.assertEqual(animating_frame.split('\n')[0], f'\r{term.normal}')

        for frame in (animating_frame, settled_frame):
            self.assertNotIn('•', frame)
            self.assertIn('Compacting my thoughts into a more manageable size', frame)
            line = next(line for line in frame.split('\n') if 'Compacting my thoughts' in line)

            self.assertTrue(line.lstrip('\r').startswith(term.bold_purple))

        self.assertNotIn(term.bold_blue, settled_frame)

    def test_tool_beat_renders_an_arrow_in_the_label_color(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(label='Reading', description='src/foo.py')
        mutating = StoryBeat(label='Executing', description='pytest -q', can_mutate_state=True)
        system = StoryBeat(label='Executing', description='pytest -q', can_affect_system=True)
        dangerous = StoryBeat(label='Executing', description='pytest -q', is_dangerous=True)

        for frame in (progress.frame(beat), progress.settled_frame(beat)):
            self.assertIn(f'{term.bold_skyblue}↳{term.normal} ', frame)

        for frame in (progress.frame(mutating), progress.settled_frame(mutating)):
            self.assertIn(f'{term.bold_purple}↳{term.normal} ', frame)

        for frame in (progress.frame(system), progress.settled_frame(system)):
            self.assertIn(f'{term.bold_orange}↳{term.normal} ', frame)

        for frame in (progress.frame(dangerous), progress.settled_frame(dangerous)):
            self.assertIn(f'{term.bold_red}↳{term.normal} ', frame)

    def test_multiline_beat_animates_folded_on_one_line(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        description = 'pytest -q\nimport blessed\nprint(1)'
        beat = StoryBeat(label='Executing', description=description)

        animating_frame = progress.frame(beat)
        next_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        animated_lines = animating_frame.split('\n')
        self.assertEqual(len(animated_lines), 4)
        self.assertIn('Executing', animated_lines[1])
        self.assertTrue(animated_lines[2].startswith(f'\r{term.bold_skyblue}↳{term.normal} '))
        self.assertIn('pytest -q import blessed print(1)', animated_lines[2])

        next_lines = next_frame.split('\n')
        self.assertEqual(len(next_lines), 2)
        self.assertTrue(next_lines[0].startswith(f'\x1b[1A\r{term.bold_skyblue}↳{term.normal} '))
        self.assertIn('pytest -q import blessed print(1)', next_lines[0])

        settled_lines = settled_frame.split('\n')
        self.assertTrue(settled_lines[0].startswith(f'\x1b[1A\r{term.bold_skyblue}↳{term.normal} '))
        for index, part in enumerate(description.split('\n')):
            self.assertIn(part, settled_lines[index])
            self.assertTrue(settled_lines[index].endswith(term.clear_eol()))

    def test_settled_frame_clears_each_overwritten_line(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        description = (
            'a long first line that overwrites the animating line\nsecond line\nthird line'
        )
        beat = StoryBeat(label='Executing', description=description)

        progress.frame(beat)
        settled = progress.settled_frame(beat)

        lines = settled.split('\n')
        self.assertEqual(len(lines), 4)
        for line in lines[:3]:
            self.assertTrue(line.endswith(term.clear_eol()))
        self.assertEqual(lines[3], '\r')

    def test_settling_after_multiple_ticks_clears_the_phrase_line(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        term = progress.term
        beat = StoryBeat(label='Reading', description='src/a.py')

        progress.frame(beat)
        progress.frame(beat)
        settled = progress.settled_frame(beat)

        lines = settled.split('\n')
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith('\x1b[1A\r'))
        self.assertTrue(lines[0].endswith(term.clear_eol()))
        self.assertEqual(lines[1], f'\r{term.clear_eol()}')

        progress.update(StoryBeat(label='Reading', description='src/b.py'))
        next_frame = progress.frame(progress.beats[-1])

        self.assertTrue(next_frame.startswith('\x1b[1A\r'))

    def test_tick_frame_animates_the_placeholder_beat_while_idle(self) -> None:
        with mock.patch(
            'dandy.interfaces.cli.tui.story_progress.thinking_phrase',
            return_value='Polishing a Cufflink',
        ):
            progress = StoryProgress(Terminal(force_styling='default'))
            frame = progress.tick_frame()
            term = progress.term

        lines = frame.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], f'\r{term.normal}{term.clear_eol()}')
        phrase_line = f'{term.bold_grey}✦ Polishing a Cufflink{term.normal}'
        self.assertIn(phrase_line, lines[1])

    def test_first_beat_settles_the_placeholder_before_animating(self) -> None:
        beat = StoryBeat(label='Reading', description='src/a.py')
        progress = StoryProgress(Terminal(force_styling='default'))

        progress.tick_frame()
        progress.update(beat)
        frame = progress.tick_frame()

        self.assertTrue(frame.startswith('\x1b[1A\r'))
        self.assertIn('Reading', frame)
        self.assertIn('src/a.py', frame)
        self.assertEqual(progress.carry_prefix(), '')

        settled = progress.settled_frame(beat)

        self.assertIn('src/a.py', settled)
        self.assertNotIn('Reading', settled)

    def test_pause_at_fresh_line_settles_and_lands_on_the_carry_line(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(label='Reading', description='src/a.py')

        progress.update(beat)
        progress.frame(beat)
        pause = progress.pause_at_fresh_line()

        self.assertTrue(pause.startswith('\x1b[1A\r'))
        self.assertTrue(pause.endswith('\x1b[1A\r'))
        self.assertIn('src/a.py', pause)
        self.assertEqual(progress.carry_prefix(), '')

        next_frame = progress.frame(StoryBeat(description='After the pause.'))
        self.assertTrue(next_frame.startswith('\r'))

        fresh = StoryProgress(Terminal(force_styling='default'))

        self.assertEqual(fresh.pause_at_fresh_line(), '\r')

    def test_pause_at_fresh_line_on_the_placeholder_clears_only_the_phrase_line(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))

        progress.tick_frame()
        pause = progress.pause_at_fresh_line()

        # The placeholder region is two lines (blank line + phrase line) and the
        # cursor sits on the phrase line after the last tick: clear just that
        # line and climb to the region's blank first line, so the prompt's own
        # leading newline leaves one blank line of separation instead of the
        # cleared animation lines piling up in the scrollback.
        self.assertEqual(pause, '\r\x1b[K\x1b[1A\r')

        progress.resume_animation()
        progress.tick_frame()
        second_pause = progress.pause_at_fresh_line()

        self.assertEqual(second_pause, '\r\x1b[K\x1b[1A\r')

    def test_resumed_placeholder_is_animating_and_keeps_the_phrase_until_a_beat(self) -> None:
        beat = StoryBeat(label='Reading', description='src/a.py')

        with mock.patch(
            'dandy.interfaces.cli.tui.story_progress.thinking_phrase',
            return_value='Polishing a Cufflink',
        ):
            progress = StoryProgress(Terminal(force_styling='default'))

            progress.tick_frame()
            self.assertTrue(progress.is_animating)

            progress.resume_animation()
            self.assertTrue(progress.is_animating)
            frame = progress.tick_frame()
            self.assertIn('✦ Polishing a Cufflink', frame)
            self.assertTrue(progress.is_animating)

            progress.update(beat)
            frame = progress.tick_frame()

            # The next real beat settles the resumed placeholder and animates
            # the beat itself instead of the leftover phrase.
            self.assertIn('src/a.py', frame)
            self.assertFalse(progress.is_animating)

    def test_settle_animation_clears_a_leftover_placeholder(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))

        # Nothing animated yet: nothing to clear.
        self.assertEqual(progress.settle_animation(), '')

        progress.tick_frame()
        settle = progress.settle_animation()

        # The phrase line is cleared and the cursor climbs back to the
        # region's blank first line, like a pause.
        self.assertEqual(settle, '\r\x1b[K\x1b[1A\r')

        # A resumed placeholder (the task ended right after a question) is
        # cleared the same way.
        progress.resume_animation()
        progress.tick_frame()
        self.assertEqual(progress.settle_animation(), '\r\x1b[K\x1b[1A\r')

        self.assertEqual(progress.settle_animation(), '')

    def test_settle_animation_is_a_no_op_for_a_live_real_beat(self) -> None:
        beat = StoryBeat(label='Reading', description='src/a.py')
        progress = StoryProgress(Terminal(force_styling='default'))

        progress.update(beat)
        progress.frame(beat)

        # The beat region is settled by the caller's settled_frame pass, not
        # by settle_animation; it must not touch it.
        self.assertEqual(progress.settle_animation(), '')
        self.assertFalse(progress.is_animating)

    def test_run_timed_task_clears_the_phrase_when_the_task_ends_after_a_question(self) -> None:
        gate = QuestionGate()

        def work(update: Callable[[StoryBeat], None]) -> object:
            gate.ask('Which color?', ['red', 'blue'])
            sleep(0.5)
            return 'done'

        def question_handler(
            question: str, choices: list[str], index: int, total: int | None
        ) -> str | None:
            return 'blue'

        self.printer.run_timed_task(
            task='pick a color', work=work, question_gate=gate, question_handler=question_handler
        )

        written = ''.join(str(call.args[0]) for call in self.mock_write.call_args_list if call.args)

        # The thinking-phrase line that animated while the model worked on the
        # answer must be cleared before the completion line prints, so it does
        # not survive as an orphan in the scrollback.
        self.assertIn(f'{self.printer.term.clear_eol()}\x1b[1A\r', written)

    def test_run_timed_task_does_not_reprint_the_settled_beat_after_the_question(self) -> None:
        gate = QuestionGate()

        def work(update: Callable[[StoryBeat], None]) -> object:
            update(StoryBeat(label='Reading', description='src/a.py'))
            sleep(0.3)
            gate.ask('Which color?', ['red', 'blue'])
            sleep(0.3)
            return 'done'

        def question_handler(
            question: str, choices: list[str], index: int, total: int | None
        ) -> str | None:
            self.mock_write.reset_mock()
            return 'blue'

        self.printer.run_timed_task(
            task='pick a color', work=work, question_gate=gate, question_handler=question_handler
        )

        written = [str(call.args[0]) for call in self.mock_write.call_args_list if call.args]

        # After the question is answered the animation must not re-emit the
        # beat that was settled above the prompt.
        self.assertNotIn('src/a.py', ''.join(written))

    def test_run_timed_task_resumes_the_thinking_animation_after_a_question(self) -> None:
        gate = QuestionGate()
        release = threading.Event()

        def work(update: Callable[[StoryBeat], None]) -> object:
            gate.ask('Which color?', ['red', 'blue'])
            release.wait()
            return 'done'

        def question_handler(
            question: str, choices: list[str], index: int, total: int | None
        ) -> str | None:
            self.mock_write.reset_mock()
            return 'blue'

        threading.Timer(0.4, release.set).start()

        with mock.patch(
            'dandy.interfaces.cli.tui.story_progress.thinking_phrase',
            return_value='Polishing a Cufflink',
        ):
            self.printer.run_timed_task(
                task='pick a color',
                work=work,
                question_gate=gate,
                question_handler=question_handler,
            )

        written = ''.join(str(call.args[0]) for call in self.mock_write.call_args_list if call.args)

        # After the answer is delivered the thinking-phrase animation restarts
        # (the placeholder region resuming) while the model works.
        self.assertIn('✦ Polishing a Cufflink', written)

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

        result = self.printer.run_timed_task(task='fix bug', work=work)

        self.assertEqual(result, {'text': 'done'})

        written = [str(call.args[0]) for call in self.mock_write.call_args_list if call.args]
        story_lines = [line for line in written if line.endswith(('\n', '\r'))]

        self.assertTrue(
            any('Reading the test file to understand it.' in line for line in story_lines)
        )
        self.assertTrue(any('"pytest -q"' in line for line in story_lines))

        printed_lines = [str(call.args[0]) for call in self.mock_print.call_args_list if call.args]
        completion_lines = [line for line in printed_lines if 'Request Completed in ' in line]

        self.assertEqual(len(completion_lines), 1)

    def test_run_timed_task_notifies_on_completion(self) -> None:
        def work(update: Callable[[StoryBeat], None]) -> object:
            return 'done'

        with (
            mock.patch('dandy.interfaces.cli.tui.notify.notifications_enabled', return_value=True),
            mock.patch(
                'dandy.interfaces.cli.tui.notify._terminal_supports_notifications',
                return_value=True,
            ),
        ):
            self.printer.run_timed_task(task='fix bug', work=work)

        written_text = ''.join(
            str(call.args[0]) for call in self.mock_write.call_args_list if call.args
        )
        self.assertNotIn('\x1b]777;', written_text)
        self.assertIn('\x1b]9;proj — Request Completed in ', written_text)

    def test_run_timed_task_failed_work_does_not_notify(self) -> None:
        def work(update: Callable[[StoryBeat], None]) -> object:
            raise RunStoppedError('Run stopped by user.')

        with self.assertRaises(RunStoppedError):
            self.printer.run_timed_task(task='stop me', work=work)

        written_text = ''.join(
            str(call.args[0]) for call in self.mock_write.call_args_list if call.args
        )
        printed_text = ''.join(
            str(call.args[0]) for call in self.mock_print.call_args_list if call.args
        )
        self.assertNotIn('\x1b]777;', written_text)
        self.assertNotIn('\x1b]9;', written_text)
        self.assertNotIn('Request Completed in ', printed_text)

    def test_run_timed_task_propagates_stop_error_from_work(self) -> None:
        def work(update: Callable[[StoryBeat], None]) -> object:
            raise RunStoppedError('Run stopped by user.')

        with self.assertRaises(RunStoppedError):
            self.printer.run_timed_task(task='stop me', work=work, stop_signal=StopSignal())

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
        queued = [escape, escape]

        def inkey_side_effect(timeout: float = 0) -> Keystroke:
            return queued.pop(0) if queued else Keystroke('')

        mock_inkey.side_effect = inkey_side_effect

        threading.Timer(0.3, release.set).start()

        result = self.printer.run_timed_task(task='stop me', work=work, stop_signal=stop_signal)

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
        queued = [Keystroke('\x1b\x1b')]

        def inkey_side_effect(timeout: float = 0) -> Keystroke:
            return queued.pop(0) if queued else Keystroke('')

        mock_inkey.side_effect = inkey_side_effect

        threading.Timer(0.3, release.set).start()

        result = self.printer.run_timed_task(task='stop me', work=work, stop_signal=stop_signal)

        self.assertEqual(result, 'done')
        self.assertTrue(stop_signal.is_set())

    @mock.patch.object(Terminal, 'inkey')
    def test_run_timed_task_single_escape_does_not_stop(self, mock_inkey: mock.MagicMock) -> None:
        stop_signal = StopSignal()
        release = threading.Event()

        def work(update: Callable[[StoryBeat], None]) -> object:
            release.wait(5)
            return 'done'

        queued = [Keystroke('\x1b'), Keystroke('a')]

        def inkey_side_effect(timeout: float = 0) -> Keystroke:
            return queued.pop(0) if queued else Keystroke('')

        mock_inkey.side_effect = inkey_side_effect

        threading.Timer(0.3, release.set).start()

        result = self.printer.run_timed_task(task='keep going', work=work, stop_signal=stop_signal)

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

        result = self.printer.run_timed_task(task='no stop', work=work)

        self.assertEqual(result, 'done')
        mock_inkey.assert_not_called()

    @mock.patch.object(Terminal, 'inkey', side_effect=OSError('no tty'))
    def test_run_timed_task_survives_unreadable_stdin(self, mock_inkey: mock.MagicMock) -> None:
        release = threading.Event()

        def work(update: Callable[[StoryBeat], None]) -> object:
            release.wait(5)
            return 'done'

        threading.Timer(0.15, release.set).start()

        result = self.printer.run_timed_task(task='no tty', work=work, stop_signal=StopSignal())

        self.assertEqual(result, 'done')

    def test_run_timed_task_delivers_a_pending_question_to_the_handler(self) -> None:
        gate = QuestionGate()
        prompts: list[tuple[str, list[str]]] = []

        def work(update: Callable[[StoryBeat], None]) -> object:
            return {'answer': gate.ask('Which color?', ['red', 'blue'])}

        def question_handler(
            question: str, choices: list[str], index: int, total: int | None
        ) -> str | None:
            prompts.append((question, choices, index, total))
            return 'blue'

        result = self.printer.run_timed_task(
            task='pick a color', work=work, question_gate=gate, question_handler=question_handler
        )

        self.assertEqual(result, {'answer': 'blue'})
        self.assertEqual(prompts, [('Which color?', ['red', 'blue'], 1, None)])
        self.assertIsNone(gate.pending)

    def test_run_timed_task_question_prompt_lands_on_a_fresh_line(self) -> None:
        gate = QuestionGate()

        def work(update: Callable[[StoryBeat], None]) -> object:
            update(StoryBeat(label='Reading', description='src/a.py'))
            sleep(0.3)
            return {'answer': gate.ask('Which color?', ['red', 'blue'])}

        def question_handler(
            question: str, choices: list[str], index: int, total: int | None
        ) -> str | None:
            written = [str(call.args[0]) for call in self.mock_write.call_args_list if call.args]
            self.assertIn(written[-1], ('\x1b[1A\r', '\r'))
            self.assertEqual(question, 'Which color?')
            self.assertEqual(choices, ['red', 'blue'])
            return 'blue'

        result = self.printer.run_timed_task(
            task='pick a color', work=work, question_gate=gate, question_handler=question_handler
        )

        self.assertEqual(result, {'answer': 'blue'})
        self.assertIsNone(gate.pending)

    def test_run_timed_task_a_none_answer_stops_the_run(self) -> None:
        gate = QuestionGate()
        stop_signal = StopSignal()

        def work(update: Callable[[StoryBeat], None]) -> object:
            gate.ask('Continue?', None, stop_signal)

            if stop_signal.is_set():
                raise RunStoppedError('Run stopped by user.')

            return 'unreachable'

        def question_handler(
            question: str, choices: list[str], index: int, total: int | None
        ) -> str | None:
            return None

        with self.assertRaises(RunStoppedError):
            self.printer.run_timed_task(
                task='stop me',
                work=work,
                stop_signal=stop_signal,
                question_gate=gate,
                question_handler=question_handler,
            )

        self.assertTrue(stop_signal.is_set())
        self.assertIsNone(gate.pending)


class TestStoryProgressHeadingGrouping(TestCase):
    def setUp(self) -> None:
        self.progress = StoryProgress(Terminal(force_styling='default'))

    def test_first_labeled_beat_gets_a_heading(self) -> None:
        beat = StoryBeat(label='Reading', description='src/a.py')
        self.progress.update(beat)

        frame = self.progress.frame(beat)

        self.assertIn('Reading', frame)
        self.assertIn('src/a.py', frame)

    def test_repeated_label_shares_the_first_heading(self) -> None:
        first = StoryBeat(label='Reading', description='src/a.py')
        second = StoryBeat(label='Reading', description='src/b.py')
        self.progress.update(first)
        self.progress.update(second)

        first_frame = self.progress.frame(first)
        first_settled = self.progress.settled_frame(first)
        second_frame = self.progress.frame(second)
        second_settled = self.progress.settled_frame(second)

        self.assertIn('Reading', first_frame)
        self.assertNotIn('Reading', first_settled)
        self.assertNotIn('Reading', second_frame)
        self.assertNotIn('Reading', second_settled)
        self.assertIn('src/a.py', first_settled)
        self.assertIn('src/b.py', second_frame)

    def test_heading_prints_once_across_animating_and_settling(self) -> None:
        beat = StoryBeat(label='Reading', description='src/a.py')

        first_frame = self.progress.frame(beat)
        second_frame = self.progress.frame(beat)
        settled = self.progress.settled_frame(beat)

        self.assertIn('Reading', first_frame)
        self.assertNotIn('Reading', second_frame)
        self.assertNotIn('Reading', settled)

    def test_label_change_emits_a_new_heading(self) -> None:
        reading = StoryBeat(label='Reading', description='src/a.py')
        writing = StoryBeat(label='Writing', description='src/b.py')
        self.progress.update(reading)
        self.progress.update(writing)

        reading_frame = self.progress.frame(reading)
        reading_settled = self.progress.settled_frame(reading)
        writing_frame = self.progress.frame(writing)

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

        self.progress.frame(reading)
        self.progress.settled_frame(reading)
        self.progress.frame(writing)
        self.progress.settled_frame(writing)
        reading_again_frame = self.progress.frame(reading_again)

        self.assertIn('Reading', reading_again_frame)
        self.assertIn('src/c.py', reading_again_frame)

    def test_non_tool_beat_breaks_the_group_and_reprints_the_label(self) -> None:
        first = StoryBeat(label='Reading', description='src/a.py')
        narration = StoryBeat(description='Let me check the other file.', kind='narration')
        second = StoryBeat(label='Reading', description='src/b.py')
        self.progress.update(first)
        self.progress.update(narration)
        self.progress.update(second)

        first_settled = self.progress.settled_frame(first)
        narration_settled = self.progress.settled_frame(narration)
        second_frame = self.progress.frame(second)

        self.assertIn('Reading', first_settled)
        self.assertNotIn('Reading', narration_settled)
        self.assertIn('Reading', second_frame)
        self.assertNotIn('•', narration_settled)

    def test_compaction_beat_also_breaks_the_group(self) -> None:
        first = StoryBeat(label='Reading', description='src/a.py')
        notice = StoryBeat(
            description='Compacting my thoughts into a more manageable size', kind='compaction'
        )
        second = StoryBeat(label='Reading', description='src/b.py')
        self.progress.update(first)
        self.progress.update(notice)
        self.progress.update(second)

        first_settled = self.progress.settled_frame(first)
        notice_settled = self.progress.settled_frame(notice)
        second_frame = self.progress.frame(second)

        self.assertIn('Reading', first_settled)
        self.assertNotIn('Reading', notice_settled)
        self.assertIn('Reading', second_frame)

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
            linked, f'Reading \x1b]8;;{expected_uri}\x1b\\src/foo.py\x1b]8;;\x1b\\ lines 1-10'
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
        progress = StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(label='Reading', description='src/foo.py lines 1-10')

        animating_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        expected_uri = (self.project_base_path / 'src' / 'foo.py').as_uri()

        for frame in (animating_frame, settled_frame):
            self.assertIn(f'\x1b]8;;{expected_uri}\x1b\\src/foo.py\x1b]8;;\x1b\\', frame)
            self.assertIn('lines 1-10', frame)

    def test_description_only_beats_are_not_linked(self) -> None:
        progress = StoryProgress(Terminal(force_styling='default'))
        beat = StoryBeat(description='Checking src/foo.py now.', kind='narration')

        animating_frame = progress.frame(beat)
        settled_frame = progress.settled_frame(beat)

        for frame in (animating_frame, settled_frame):
            self.assertNotIn('\x1b]8', frame)


class TestPrinterFileChangeSections(TestCase):
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

    @property
    def printed_lines(self) -> list[str]:
        return [call.args[0] if call.args else '' for call in self.mock_print.call_args_list]

    def _expected_link(self, relative_path: str) -> str:
        expected_uri = (self.project_base_path / relative_path).as_uri()
        return f'\x1b]8;;{expected_uri}\x1b\\{relative_path}\x1b]8;;\x1b\\'

    def test_all_empty_prints_nothing(self) -> None:
        self.printer.file_change_sections([], [], [])

        self.mock_print.assert_not_called()

    def test_section_prints_heading_border_bullet_and_link(self) -> None:
        self.printer.file_change_sections(['src/foo.py'], [], [])

        lines = self.printed_lines
        term = self.printer.term

        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], '')
        self.assertEqual(lines[1], f'{term.bold_blue}Added Files{term.normal}')
        self.assertEqual(lines[2], term.blue('─' * term.width))
        self.assertEqual(
            lines[3],
            f'{term.normal}{term.green}◈ {term.normal} {self._expected_link("src/foo.py")}',
        )

    def test_bullets_are_colored_per_action(self) -> None:
        self.printer.file_change_sections(['src/a.py'], ['src/b.py'], ['src/c.py'])

        lines = self.printed_lines
        term = self.printer.term
        bullet_lines = [line for line in lines if '◈' in line]

        self.assertEqual(len(bullet_lines), 3)
        self.assertIn(f'{term.green}◈ {term.normal}', bullet_lines[0])
        self.assertIn(f'{term.purple}◈ {term.normal}', bullet_lines[1])
        self.assertIn(f'{term.red}◈ {term.normal}', bullet_lines[2])

    def test_sections_print_in_order_and_skip_empty(self) -> None:
        self.printer.file_change_sections(['src/a.py'], [], ['src/c.py'])

        lines = self.printed_lines
        term = self.printer.term

        self.assertEqual(len(lines), 8)
        self.assertEqual(lines[0], '')
        self.assertEqual(lines[1], f'{term.bold_blue}Added Files{term.normal}')
        self.assertEqual(lines[4], '')
        self.assertEqual(lines[5], f'{term.bold_blue}Removed Files{term.normal}')
        self.assertNotIn('Modified Files', '\n'.join(lines))

    def test_empty_line_before_each_section(self) -> None:
        self.printer.file_change_sections(['src/a.py'], ['src/b.py'], ['src/c.py'])

        lines = self.printed_lines
        term = self.printer.term

        self.assertEqual(len(lines), 12)
        self.assertEqual(lines[0], '')
        self.assertEqual(lines[4], '')
        self.assertEqual(lines[8], '')
        self.assertIn(f'{term.red}◈ {term.normal}', lines[11])
