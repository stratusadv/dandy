from unittest import TestCase, mock

from blessed import Terminal

from dandy.interfaces.cli.tui.tui import tui
from tests.interfaces.cli.intelligence.screen import MiniScreen, ScreenStdout


class FakeKey(str):
    def __new__(cls, value: str, name: str) -> 'FakeKey':
        obj = super().__new__(cls, value)
        obj.name = name
        obj.is_sequence = False
        return obj


ESCAPE_KEY = FakeKey('\x1b', 'KEY_ESCAPE')
ENTER_KEY = FakeKey('\n', 'KEY_ENTER')
TAB_KEY = FakeKey('\t', 'KEY_TAB')
BACKSPACE_KEY = FakeKey('\x7f', 'KEY_BACKSPACE')


class TestTuiEscapeExit(TestCase):
    def setUp(self) -> None:
        self.cbreak_patch = mock.patch.object(tui.term, 'cbreak')
        self.cbreak_patch.start()
        self.addCleanup(self.cbreak_patch.stop)

    @mock.patch('sys.stdout.write')
    def test_get_user_input_returns_none_on_double_escape(self, mock_write) -> None:
        with mock.patch.object(tui.term, 'inkey', side_effect=[ESCAPE_KEY, ESCAPE_KEY]):
            result = tui.get_user_input()

        self.assertIsNone(result)

    @mock.patch('sys.stdout.write')
    def test_single_escape_does_not_exit(self, mock_write) -> None:
        with mock.patch.object(
            tui.term, 'inkey', side_effect=[ESCAPE_KEY, FakeKey('a', None), ENTER_KEY]
        ):
            # 'a' resets the escape count, so the trailing text is returned.
            tui._escape_exit = False
            result = tui.get_user_input()

        self.assertEqual(result, 'a')


class TestTuiChoices(TestCase):
    def setUp(self) -> None:
        self.cbreak_patch = mock.patch.object(tui.term, 'cbreak')
        self.cbreak_patch.start()
        self.addCleanup(self.cbreak_patch.stop)

        self.print_patch = mock.patch('builtins.print')
        self.mock_print = self.print_patch.start()
        self.addCleanup(self.print_patch.stop)

    @mock.patch('sys.stdout.write')
    def test_choice_number_selects_the_choice(self, mock_write) -> None:
        with mock.patch.object(tui.term, 'inkey', side_effect=[FakeKey('2', None), ENTER_KEY]):
            result = tui.get_user_input(question='Which color?', choices=['red', 'blue'])

        self.assertEqual(result, 'blue')

    @mock.patch('sys.stdout.write')
    def test_free_text_is_returned_verbatim(self, mock_write) -> None:
        keys = [FakeKey(letter, None) for letter in 'green'] + [ENTER_KEY]

        with mock.patch.object(tui.term, 'inkey', side_effect=keys):
            result = tui.get_user_input(question='Which color?', choices=['red', 'blue'])

        self.assertEqual(result, 'green')

    @mock.patch('sys.stdout.write')
    def test_out_of_range_number_returns_the_raw_text(self, mock_write) -> None:
        with mock.patch.object(tui.term, 'inkey', side_effect=[FakeKey('5', None), ENTER_KEY]):
            result = tui.get_user_input(question='Which color?', choices=['red'])

        self.assertEqual(result, '5')

    @mock.patch('sys.stdout.write')
    def test_number_without_choices_is_plain_text(self, mock_write) -> None:
        with mock.patch.object(tui.term, 'inkey', side_effect=[FakeKey('1', None), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, '1')

    @mock.patch('sys.stdout.write')
    def test_choices_are_printed_numbered_under_the_question(
        self, mock_write: mock.MagicMock
    ) -> None:
        with mock.patch.object(tui.term, 'inkey', side_effect=[ESCAPE_KEY, ESCAPE_KEY]):
            result = tui.get_user_input(question='Which color?', choices=['red', 'blue'])

        self.assertIsNone(result)

        printed = ' '.join(
            str(call.args[0]) for call in self.mock_print.call_args_list if call.args
        )

        self.assertIn('Which color?', printed)
        self.assertIn('Asking', printed)
        self.assertIn('↳', printed)
        self.assertIn('1) red', printed)
        self.assertIn('2) blue', printed)
        self.assertNotIn('Question: ', printed)


class TestTuiQuestionPrompt(TestCase):
    def setUp(self) -> None:
        self.term = Terminal(force_styling='default')
        self.term_patch = mock.patch.object(tui, 'term', self.term)
        self.term_patch.start()
        self.addCleanup(self.term_patch.stop)

        self.printer_term_patch = mock.patch.object(tui.printer, 'term', self.term)
        self.printer_term_patch.start()
        self.addCleanup(self.printer_term_patch.stop)

        self.cbreak_patch = mock.patch.object(self.term, 'cbreak')
        self.cbreak_patch.start()
        self.addCleanup(self.cbreak_patch.stop)

        self.print_patch = mock.patch('builtins.print')
        self.mock_print = self.print_patch.start()
        self.addCleanup(self.print_patch.stop)

    def _printed_lines(self) -> list[str]:
        return [str(call.args[0]) for call in self.mock_print.call_args_list if call.args]

    @mock.patch('sys.stdout.write')
    def test_question_prints_label_then_arrow_and_question_on_one_line(
        self, mock_write: mock.MagicMock
    ) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[ESCAPE_KEY, ESCAPE_KEY]):
            result = tui.get_user_input(question='Which color?', choices=['red', 'blue'])

        self.assertIsNone(result)

        printed = self._printed_lines()
        term = self.term

        self.assertEqual(len(printed), 6)
        self.assertEqual(
            printed[0], f'{term.normal}\n{term.purple}Asking{term.normal}{term.normal}'
        )
        self.assertEqual(
            printed[1], f'{term.normal}{term.purple}↳{term.normal} Which color?{term.normal}'
        )
        self.assertIn('1)', printed[2])
        self.assertIn('red', printed[2])
        self.assertIn('2)', printed[3])
        self.assertIn('blue', printed[3])
        self.assertEqual(printed[4], term.purple('─' * term.width))
        self.assertEqual(printed[5], term.purple('─' * term.width))
        mock_write.assert_any_call(term.purple('⦿ '))

    @mock.patch('sys.stdout.write')
    def test_question_label_and_arrow_are_plain_purple_and_text_is_plain_black(
        self, mock_write: mock.MagicMock
    ) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[ESCAPE_KEY, ESCAPE_KEY]):
            tui.get_user_input(question='Which color?', choices=['red', 'blue'])

        full = '\n'.join(self._printed_lines())
        term = self.term

        self.assertIn(f'{term.purple}Asking', full)
        self.assertIn(f'{term.purple}↳{term.normal} Which color?', full)
        self.assertIn(f'{term.purple}1)', full)
        self.assertIn(f'{term.purple}2)', full)
        self.assertNotIn(term.bold_purple, full)
        self.assertNotIn(term.bold_skyblue, full)
        self.assertNotIn(term.bold_grey, full)
        self.assertNotIn(term.bold_orange, full)
        mock_write.assert_any_call(term.purple('⦿ '))


class TestTuiCommandCompletion(TestCase):
    def setUp(self) -> None:
        self.term = Terminal(force_styling='default')
        self.term_patch = mock.patch.object(tui, 'term', self.term)
        self.term_patch.start()
        self.addCleanup(self.term_patch.stop)

        self.printer_term_patch = mock.patch.object(tui.printer, 'term', self.term)
        self.printer_term_patch.start()
        self.addCleanup(self.printer_term_patch.stop)

        self.cbreak_patch = mock.patch.object(self.term, 'cbreak')
        self.cbreak_patch.start()
        self.addCleanup(self.cbreak_patch.stop)

        self.print_patch = mock.patch('builtins.print')
        self.mock_print = self.print_patch.start()
        self.addCleanup(self.print_patch.stop)

    @staticmethod
    def _keys(text: str) -> list[FakeKey]:
        return [FakeKey(char, None) for char in text]

    @staticmethod
    def _written(mock_write: mock.MagicMock) -> list[str]:
        return [str(call.args[0]) for call in mock_write.call_args_list if call.args]

    @staticmethod
    def _all_commands_suggestion(term: Terminal) -> str:
        return term.grey('  /init   /new   /sessions   /resume   /delete   /quit')

    @mock.patch('sys.stdout.write')
    def test_slash_shows_all_commands_inline(self, mock_write: mock.MagicMock) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/'), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, '/')

        expected = (
            '\r'
            + self.term.clear_eol()
            + self.term.bold_blue('⦿ ')
            + '/'
            + self._all_commands_suggestion(self.term)
        )
        written = self._written(mock_write)

        self.assertIn(expected, written)

    @mock.patch('sys.stdout.write')
    def test_typing_narrows_the_suggestions(self, mock_write: mock.MagicMock) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/s'), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, '/s')

        narrowed = [
            write
            for write in self._written(mock_write)
            if self.term.grey('  /sessions') in write and '/init' not in write
        ]

        self.assertTrue(narrowed)

    @mock.patch('sys.stdout.write')
    def test_space_hides_the_suggestions(self, mock_write: mock.MagicMock) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/s x'), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, '/s x')

        written = self._written(mock_write)
        space_redraw = '\r' + self.term.clear_eol() + self.term.bold_blue('⦿ ') + '/s '
        space_index = written.index(space_redraw)

        for write in written[space_index + 1 :]:
            self.assertNotIn('sessions', write)

    @mock.patch('sys.stdout.write')
    def test_unknown_prefix_shows_no_suggestion(self, mock_write: mock.MagicMock) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/x'), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, '/x')

        written = self._written(mock_write)
        unknown_redraw = '\r' + self.term.clear_eol() + self.term.bold_blue('⦿ ') + '/x'
        unknown_index = written.index(unknown_redraw)

        for write in written[unknown_index + 1 :]:
            self.assertNotIn('/init', write)

    @mock.patch('sys.stdout.write')
    def test_plain_text_shows_no_suggestion(self, mock_write: mock.MagicMock) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('hi'), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, 'hi')

        for write in self._written(mock_write):
            self.assertNotIn('/init', write)

    @mock.patch('sys.stdout.write')
    def test_question_prompt_shows_no_suggestion(self, mock_write: mock.MagicMock) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/'), ENTER_KEY]):
            result = tui.get_user_input(question='Which?', choices=['a'])

        self.assertEqual(result, '/')

        for write in self._written(mock_write):
            self.assertNotIn('/init', write)

    @mock.patch('sys.stdout.write')
    def test_tab_completes_a_unique_command(self, mock_write: mock.MagicMock) -> None:
        keys = [*self._keys('/q'), TAB_KEY, ENTER_KEY]

        with mock.patch.object(self.term, 'inkey', side_effect=keys):
            result = tui.get_user_input()

        self.assertEqual(result, '/quit')
        self.assertIn(self.term.bold_blue('⦿ ') + '/quit', ''.join(self._written(mock_write)))

    @mock.patch('sys.stdout.write')
    def test_typing_a_short_shows_the_full_command_suggestion(
        self, mock_write: mock.MagicMock
    ) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/i'), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, '/i')

        narrowed = [
            write
            for write in self._written(mock_write)
            if self.term.grey('  /init') in write and '/new' not in write
        ]

        self.assertTrue(narrowed)

    @mock.patch('sys.stdout.write')
    def test_typing_a_short_hides_commands_that_only_match_by_name(
        self, mock_write: mock.MagicMock
    ) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/d'), ENTER_KEY]):
            result = tui.get_user_input()

        self.assertEqual(result, '/d')

        narrowed = [
            write
            for write in self._written(mock_write)
            if self.term.grey('  /delete') in write and '/sessions' not in write
        ]

        self.assertTrue(narrowed)

    @mock.patch('sys.stdout.write')
    def test_tab_completes_a_short_form_to_the_full_name(self, mock_write: mock.MagicMock) -> None:
        keys = [*self._keys('/s'), TAB_KEY, ENTER_KEY]

        with mock.patch.object(self.term, 'inkey', side_effect=keys):
            result = tui.get_user_input()

        self.assertEqual(result, '/sessions')
        self.assertIn(self.term.bold_blue('⦿ ') + '/sessions', ''.join(self._written(mock_write)))

    @mock.patch('sys.stdout.write')
    def test_tab_completes_the_resume_short_to_the_full_name(
        self, mock_write: mock.MagicMock
    ) -> None:
        keys = [*self._keys('/r'), TAB_KEY, ENTER_KEY]

        with mock.patch.object(self.term, 'inkey', side_effect=keys):
            result = tui.get_user_input()

        self.assertEqual(result, '/resume')
        self.assertIn(self.term.bold_blue('⦿ ') + '/resume', ''.join(self._written(mock_write)))

    @mock.patch('sys.stdout.write')
    def test_tab_keeps_an_ambiguous_prefix(self, mock_write: mock.MagicMock) -> None:
        keys = [*self._keys('/'), TAB_KEY, ENTER_KEY]

        with mock.patch.object(self.term, 'inkey', side_effect=keys):
            result = tui.get_user_input()

        self.assertEqual(result, '/')
        self.assertNotIn(self.term.bold_blue('⦿ ') + '/', self._written(mock_write))

    @mock.patch('sys.stdout.write')
    def test_tab_ignores_an_unknown_prefix(self, mock_write: mock.MagicMock) -> None:
        keys = [*self._keys('/x'), TAB_KEY, ENTER_KEY]

        with mock.patch.object(self.term, 'inkey', side_effect=keys):
            result = tui.get_user_input()

        self.assertEqual(result, '/x')
        self.assertNotIn(self.term.bold_blue('⦿ ') + '/x', self._written(mock_write))

    @mock.patch('sys.stdout.write')
    def test_tab_after_a_space_leaves_the_text_unchanged(self, mock_write: mock.MagicMock) -> None:
        keys = [*self._keys('/resume '), TAB_KEY, ENTER_KEY]

        with mock.patch.object(self.term, 'inkey', side_effect=keys):
            result = tui.get_user_input()

        self.assertEqual(result, '/resume ')
        self.assertNotIn(self.term.bold_blue('⦿ ') + '/resume ', self._written(mock_write))

    @mock.patch('sys.stdout.write')
    def test_backspace_updates_the_suggestions(self, mock_write: mock.MagicMock) -> None:
        keys = [*self._keys('/s'), BACKSPACE_KEY, ENTER_KEY]

        with mock.patch.object(self.term, 'inkey', side_effect=keys):
            result = tui.get_user_input()

        self.assertEqual(result, '/')

        written = self._written(mock_write)
        s_write = (
            '\r'
            + self.term.clear_eol()
            + self.term.bold_blue('⦿ ')
            + '/s'
            + self.term.grey('  /sessions')
        )
        s_index = written.index(s_write)
        backspace_write = (
            '\r'
            + self.term.clear_eol()
            + self.term.bold_blue('⦿ ')
            + '/'
            + self._all_commands_suggestion(self.term)
        )

        self.assertEqual(written[s_index + 1], backspace_write)

    @mock.patch('sys.stdout.write')
    def test_suggestion_is_cleared_on_enter(self, mock_write: mock.MagicMock) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[*self._keys('/'), ENTER_KEY]):
            tui.get_user_input()

        written = self._written(mock_write)
        suggestion_index = next(index for index, write in enumerate(written) if 'sessions' in write)

        self.assertEqual(
            written[suggestion_index + 1 :],
            ['\r' + self.term.clear_eol() + self.term.bold_blue('⦿ ') + '/', '\n'],
        )

    def test_render_writes_the_suggestion_inline(self) -> None:
        tui._input_prefix = self.term.bold_blue('⦿ ')
        tui._buffer = ['/', 's']
        tui._suggestions_enabled = True
        tui._suggestion_visible = False

        with mock.patch('sys.stdout.write') as mock_write:
            tui._render()

        written = [str(call.args[0]) for call in mock_write.call_args_list if call.args]

        self.assertEqual(
            written,
            [
                '\r'
                + self.term.clear_eol()
                + self.term.bold_blue('⦿ ')
                + '/s'
                + self.term.grey('  /sessions')
            ],
        )
        self.assertTrue(tui._suggestion_visible)

    def test_render_clears_the_suggestion_when_matches_go_away(self) -> None:
        tui._input_prefix = self.term.bold_blue('⦿ ')
        tui._buffer = ['/', 'x']
        tui._suggestions_enabled = True
        tui._suggestion_visible = True

        with mock.patch('sys.stdout.write') as mock_write:
            tui._render()

        written = [str(call.args[0]) for call in mock_write.call_args_list if call.args]

        self.assertEqual(written, ['\r' + self.term.clear_eol() + self.term.bold_blue('⦿ ') + '/x'])
        self.assertFalse(tui._suggestion_visible)

    def test_clear_suggestion_render_omits_the_suggestion(self) -> None:
        tui._input_prefix = self.term.bold_blue('⦿ ')
        tui._buffer = ['/']
        tui._suggestions_enabled = True
        tui._suggestion_visible = True

        with mock.patch('sys.stdout.write') as mock_write:
            tui._render(clear_suggestion=True)

        written = [str(call.args[0]) for call in mock_write.call_args_list if call.args]

        self.assertEqual(written, ['\r' + self.term.clear_eol() + self.term.bold_blue('⦿ ') + '/'])
        self.assertFalse(tui._suggestion_visible)


class TestTuiCommandCompletionScreen(TestCase):
    def setUp(self) -> None:
        self.term = Terminal(force_styling='default')
        self.term_patch = mock.patch.object(tui, 'term', self.term)
        self.term_patch.start()
        self.addCleanup(self.term_patch.stop)

        self.printer_term_patch = mock.patch.object(tui.printer, 'term', self.term)
        self.printer_term_patch.start()
        self.addCleanup(self.printer_term_patch.stop)

        self.cbreak_patch = mock.patch.object(self.term, 'cbreak')
        self.cbreak_patch.start()
        self.addCleanup(self.cbreak_patch.stop)

    @staticmethod
    def _keys(text: str) -> list[FakeKey]:
        return [FakeKey(char, None) for char in text]

    def _run_prompt_with_snapshot(
        self, keys: list[FakeKey], char_widths: dict[str, int] | None = None
    ) -> tuple[str | None, MiniScreen, str]:
        screen = MiniScreen(char_widths=char_widths)
        key_iter = iter(keys)
        snapshots: list[str] = []

        def next_key(*_args: object, **_kwargs: object) -> FakeKey:
            key = next(key_iter)

            if key is ENTER_KEY:
                snapshots.append(screen.text())

            return key

        with (
            mock.patch.object(self.term, 'inkey', side_effect=next_key),
            mock.patch('sys.stdout', ScreenStdout(screen)),
        ):
            result = tui.get_user_input()

        return result, screen, snapshots[-1]

    @staticmethod
    def _last_bullet_row(screen: MiniScreen) -> str:
        bullet_rows = [
            screen.line(row) for row in range(screen.height) if screen.line(row).startswith('⦿')
        ]

        return bullet_rows[-1]

    def test_input_line_stays_intact_when_the_bullet_renders_wide(self) -> None:
        keys = [*self._keys('/qu'), BACKSPACE_KEY, ENTER_KEY]

        result, screen, snapshot = self._run_prompt_with_snapshot(keys, char_widths={'⦿': 2})

        self.assertEqual(result, '/q')
        self.assertIn('⦿  /q  /quit', snapshot.splitlines())
        self.assertEqual(self._last_bullet_row(screen), '⦿  /q')
        self.assertNotIn('quit', screen.text())

    def test_tab_completion_stays_intact_when_the_bullet_renders_wide(self) -> None:
        keys = [*self._keys('/q'), TAB_KEY, ENTER_KEY]

        result, screen, snapshot = self._run_prompt_with_snapshot(keys, char_widths={'⦿': 2})

        self.assertEqual(result, '/quit')
        self.assertIn('⦿  /quit  /quit', snapshot.splitlines())
        self.assertEqual(self._last_bullet_row(screen), '⦿  /quit')
        self.assertNotIn('sessions', screen.text())

    def test_keystrokes_leave_no_gaps_in_the_input_line(self) -> None:
        keys = [*self._keys('/ses'), ENTER_KEY]

        result, screen, snapshot = self._run_prompt_with_snapshot(keys, char_widths={'⦿': 2})

        self.assertEqual(result, '/ses')
        self.assertIn('⦿  /ses  /sessions', snapshot.splitlines())
        self.assertEqual(self._last_bullet_row(screen), '⦿  /ses')
        self.assertNotIn('sessions', screen.text())

    def test_input_line_stays_intact_when_the_bullet_renders_narrow(self) -> None:
        keys = [*self._keys('/qu'), BACKSPACE_KEY, ENTER_KEY]

        result, screen, snapshot = self._run_prompt_with_snapshot(keys)

        self.assertEqual(result, '/q')
        self.assertIn('⦿ /q  /quit', snapshot.splitlines())
        self.assertEqual(self._last_bullet_row(screen), '⦿ /q')
        self.assertNotIn('quit', screen.text())

    def test_suggestion_renders_inline_after_the_input(self) -> None:
        keys = [*self._keys('/s'), ENTER_KEY]

        result, screen, snapshot = self._run_prompt_with_snapshot(keys)

        self.assertEqual(result, '/s')
        self.assertIn('⦿ /s  /sessions', snapshot.splitlines())
        self.assertEqual(self._last_bullet_row(screen), '⦿ /s')
        self.assertNotIn('sessions', screen.text())


class TestTuiMultiLineInput(TestCase):
    def setUp(self) -> None:
        self.screen_width = 12

        self.term = Terminal(force_styling='default')
        self.term_patch = mock.patch.object(tui, 'term', self.term)
        self.term_patch.start()
        self.addCleanup(self.term_patch.stop)

        self.printer_term_patch = mock.patch.object(tui.printer, 'term', self.term)
        self.printer_term_patch.start()
        self.addCleanup(self.printer_term_patch.stop)

        # The Tui measures wraps against term.width, so the emulated screen
        # must be exactly as wide as the terminal it is told it is.
        self.width_patch = mock.patch.object(
            Terminal, 'width', mock.PropertyMock(return_value=self.screen_width)
        )
        self.width_patch.start()
        self.addCleanup(self.width_patch.stop)

        self.cbreak_patch = mock.patch.object(self.term, 'cbreak')
        self.cbreak_patch.start()
        self.addCleanup(self.cbreak_patch.stop)

    @staticmethod
    def _keys(text: str) -> list[FakeKey]:
        return [FakeKey(char, None) for char in text]

    def _run(self, keys: list[FakeKey]) -> tuple[str | None, MiniScreen, list[str]]:
        screen = MiniScreen(width=self.screen_width)
        key_iter = iter(keys)
        snapshots: list[str] = []

        def next_key(*_args: object, **_kwargs: object) -> FakeKey:
            key = next(key_iter)
            snapshots.append(screen.text())
            return key

        with (
            mock.patch.object(self.term, 'inkey', side_effect=next_key),
            mock.patch('sys.stdout', ScreenStdout(screen)),
        ):
            result = tui.get_user_input()

        return result, screen, snapshots

    def test_typing_past_one_line_and_backspacing_leaves_no_duplicate_rows(self) -> None:
        # The prompt bullet takes two cells, so the row fills at ten buffer
        # characters.
        keys = [*self._keys('abcdefghij'), *self._keys('kl'), BACKSPACE_KEY, ENTER_KEY]

        result, screen, snapshots = self._run(keys)

        self.assertEqual(result, 'abcdefghijk')

        # The snapshot taken while inkey returns a key shows the screen as
        # the keys before it rendered it.
        expected = ''

        for index, key in enumerate(keys):
            snapshot = snapshots[index]

            # After wrapping, every keystroke must leave each typed character
            # exactly once on screen: the old bug re-typed the whole line from
            # the wrapped row and left the row above behind as a duplicate.
            for char in set(expected):
                self.assertEqual(snapshot.count(char), 1, f'duplicate rows in {snapshot!r}')

            if key is ENTER_KEY:
                continue

            expected = expected[:-1] if key is BACKSPACE_KEY else expected + key

        self.assertEqual(screen.line(0), '─' * self.screen_width)
        self.assertEqual(screen.line(1), '⦿ abcdefghij')
        self.assertEqual(screen.line(2), 'k')
        self.assertEqual(screen.line(3), '─' * self.screen_width)

    def test_backspacing_across_wrap_boundaries_keeps_the_screen_compact(self) -> None:
        typed = 'abcdefghijklmnopqrstuvwxyz0123'
        keys = [*self._keys(typed)]
        keys += [BACKSPACE_KEY] * (len(typed) - 9)
        keys.append(ENTER_KEY)

        result, screen, snapshots = self._run(keys)

        self.assertEqual(result, 'abcdefghi')

        # The snapshot taken while inkey returns a key shows the screen as
        # the keys before it rendered it.
        expected = ''

        for index, key in enumerate(keys):
            snapshot = snapshots[index]

            for char in set(expected):
                self.assertEqual(snapshot.count(char), 1, f'duplicate rows in {snapshot!r}')

            # The divider above the prompt is the only non-input row (the
            # closing one prints after the loop ends); the block itself
            # takes one row per twelve cells, the prompt bullet costing two
            # of them.
            rows = [line for line in snapshot.splitlines() if line]
            self.assertEqual(len(rows), 1 + (len(expected) + 13) // 12, f'unexpected {snapshot!r}')

            if key is ENTER_KEY:
                continue

            expected = expected[:-1] if key is BACKSPACE_KEY else expected + key

        self.assertEqual(screen.line(1), '⦿ abcdefghi')
        self.assertEqual(screen.line(2), '─' * self.screen_width)

    def test_wrapped_input_wraps_at_the_row_boundary_exactly(self) -> None:
        keys = [*self._keys('abcdefghijklmnopqrstuvwxyz0123'), ENTER_KEY]

        result, screen, _snapshots = self._run(keys)

        self.assertEqual(result, 'abcdefghijklmnopqrstuvwxyz0123')
        self.assertEqual(screen.line(1), '⦿ abcdefghij')
        self.assertEqual(screen.line(2), 'klmnopqrstuv')
        self.assertEqual(screen.line(3), 'wxyz0123')
        self.assertEqual(screen.line(4), '─' * self.screen_width)

    def test_wrapped_input_then_wrapped_backspace_clears_the_released_row(self) -> None:
        keys = [*self._keys('abcdefghijkl'), BACKSPACE_KEY, BACKSPACE_KEY, BACKSPACE_KEY, ENTER_KEY]

        result, screen, snapshots = self._run(keys)

        self.assertEqual(result, 'abcdefghi')

        # The moment the buffer falls back to one row, the second row must
        # be cleared in the same redraw (only the closing divider may sit
        # below the block).
        self.assertEqual(screen.line(1), '⦿ abcdefghi')
        self.assertEqual(screen.line(2), '─' * self.screen_width)
        self.assertNotIn('kl', snapshots[-1])
