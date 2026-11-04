from unittest import TestCase, mock

from dandy.interfaces.cli.tui.tui import tui


class FakeKey(str):
    def __new__(cls, value: str, name: str) -> 'FakeKey':
        obj = super().__new__(cls, value)
        obj.name = name
        obj.is_sequence = False
        return obj


ESCAPE_KEY = FakeKey('\x1b', 'KEY_ESCAPE')
ENTER_KEY = FakeKey('\n', 'KEY_ENTER')


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
    def test_choices_are_printed_numbered_under_the_question(self, mock_write) -> None:
        with mock.patch.object(tui.term, 'inkey', side_effect=[ESCAPE_KEY, ESCAPE_KEY]):
            result = tui.get_user_input(question='Which color?', choices=['red', 'blue'])

        self.assertIsNone(result)

        printed = ' '.join(
            str(call.args[0]) for call in self.mock_print.call_args_list if call.args
        )

        self.assertIn('Question: Which color?', printed)
        self.assertIn('1) red', printed)
        self.assertIn('2) blue', printed)
