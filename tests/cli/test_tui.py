from unittest import TestCase, mock

from dandy.cli.tui.tui import tui


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
