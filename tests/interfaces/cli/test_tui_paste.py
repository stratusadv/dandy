from unittest import TestCase, mock

from blessed.keyboard import Keystroke

from dandy.interfaces.cli.tui.tui import paste_block_indicator, tui


class FakeKey(str):
    def __new__(cls, value: str, name: str) -> 'FakeKey':
        obj = super().__new__(cls, value)
        obj.name = name
        obj.is_sequence = False
        return obj


class FakeSequence(Keystroke):
    def __new__(cls, value: str, name: str = None) -> 'FakeSequence':
        return super().__new__(cls, value, name=name)


ENTER_KEY = FakeKey('\n', 'KEY_ENTER')
BACKSPACE_KEY = FakeKey('\x7f', 'KEY_BACKSPACE')
ESCAPE_KEY = FakeKey('\x1b', 'KEY_ESCAPE')


def _chars(text: str) -> list[FakeKey]:
    return [FakeKey(char, None) for char in text]


def _csi(value: str, name: str | None = None) -> FakeSequence:
    return FakeSequence(value, name)


def _full_paste_key(text: str) -> FakeSequence:
    key = FakeSequence('\x1b[200~', 'BRACKETED_PASTE')
    key._mode = 2004
    key._name = 'BRACKETED_PASTE'
    type(key).text = property(lambda self: text)

    return key


def _run_prompt(keys: list, kbhit: bool = True) -> str | None:
    tui._pending_marker = ''
    tui._inside_bracketed_paste = False
    tui._buffer = []
    tui._paste_blocks = set()
    tui._escape_count = 0

    with (
        mock.patch.object(tui.term, 'inkey', side_effect=list(keys)),
        mock.patch.object(tui.term, 'kbhit', return_value=kbhit),
        mock.patch.object(tui.term, 'cbreak'),
        mock.patch.object(tui.term, 'bracketed_paste'),
        mock.patch('sys.stdout.write'),
    ):
        return tui.get_user_input()


class TestPasteBlockIndicator(TestCase):
    def test_single_line_indicator(self) -> None:
        self.assertEqual(paste_block_indicator('one line'), '⤶ 1 lines · 8 B pasted')

    def test_multi_line_indicator_counts_newlines(self) -> None:
        self.assertEqual(paste_block_indicator('a\nb\nc'), '⤶ 3 lines · 5 B pasted')

    def test_large_paste_uses_kilobytes(self) -> None:
        self.assertIn('KB', paste_block_indicator('x' * 2048))


class TestTuiBracketedPaste(TestCase):
    def setUp(self) -> None:
        self.notifications_patch = mock.patch(
            'dandy.interfaces.cli.tui.notify.notifications_enabled', return_value=False
        )
        self.notifications_patch.start()
        self.addCleanup(self.notifications_patch.stop)

    def test_paste_newlines_arrive_as_one_message_not_one_per_line(self) -> None:
        keys = [
            ESCAPE_KEY,
            _csi('[200~', 'CSI'),
            *_chars('line one\nline two\nline three\n'),
            ESCAPE_KEY,
            _csi('[201~', 'CSI'),
            ENTER_KEY,
        ]

        result = _run_prompt(keys)

        self.assertEqual(result, 'line one\nline two\nline three\n')

    def test_split_paste_marker_across_inkey_calls_is_recognized(self) -> None:
        # The terminal sends the marker as two bursts: a bare ESC, then the
        # CSI tail that blessed resolves as a lone CSI sequence.
        keys = [
            ESCAPE_KEY,
            _csi('[200~', 'CSI'),
            *_chars('a\nb'),
            ESCAPE_KEY,
            _csi('[201~', 'CSI'),
            ENTER_KEY,
        ]

        result = _run_prompt(keys, kbhit=False)

        self.assertEqual(result, 'a\nb')

    def test_full_paste_keystroke_from_blessed_is_one_block(self) -> None:
        keys = [_full_paste_key('first\nsecond'), ENTER_KEY]

        result = _run_prompt(keys)

        self.assertEqual(result, 'first\nsecond')
        self.assertEqual(len(tui._buffer), 1)

    def test_enter_after_a_stale_escape_still_submits(self) -> None:
        # A typed newline while the held escape is pending flushes the escape
        # (swallowed) and then submits the input.
        keys = [*_chars('hello'), ESCAPE_KEY, ENTER_KEY]

        result = _run_prompt(keys, kbhit=False)

        self.assertEqual(result, 'hello')

    def test_typed_characters_after_a_stale_escape_land_in_the_input(self) -> None:
        # The user presses escape, then types a character that is not part of
        # a paste marker: the held escape is flushed (the ESC is swallowed,
        # like a stray escape) and the character lands in the input.
        keys = [ESCAPE_KEY, *_chars('z'), ENTER_KEY]

        result = _run_prompt(keys, kbhit=False)

        self.assertEqual(result, 'z')

    def test_completing_the_start_marker_by_hand_opens_a_paste(self) -> None:
        # If the typed bytes really do spell the start marker, they are
        # treated as a paste boundary (the content comes after the marker).
        keys = [
            ESCAPE_KEY,
            _csi('[200~', 'CSI'),
            *_chars('x'),
            ESCAPE_KEY,
            _csi('[201~', 'CSI'),
            ENTER_KEY,
        ]

        result = _run_prompt(keys)

        self.assertEqual(result, 'x')

    def test_paste_block_renders_the_indicator_not_the_text(self) -> None:
        written: list[str] = []
        keys = [
            ESCAPE_KEY,
            _csi('[200~', 'CSI'),
            *_chars('secret\ncontent'),
            ESCAPE_KEY,
            _csi('[201~', 'CSI'),
            ENTER_KEY,
        ]

        with (
            mock.patch.object(tui.term, 'inkey', side_effect=list(keys)),
            mock.patch.object(tui.term, 'kbhit', return_value=True),
            mock.patch.object(tui.term, 'cbreak'),
            mock.patch.object(tui.term, 'bracketed_paste'),
            mock.patch('sys.stdout.write', side_effect=written.append),
        ):
            result = tui.get_user_input()

        self.assertEqual(result, 'secret\ncontent')
        self.assertIn('2 lines', ''.join(written))
        self.assertNotIn('secret', ''.join(written))

    def test_backspace_removes_the_whole_paste_block(self) -> None:
        # One backspace after the paste wipes the entire block, leaving an
        # empty input; a second backspace on the empty input is a no-op and
        # double-escape exits (an empty line is never submitted).
        keys = [
            ESCAPE_KEY,
            _csi('[200~', 'CSI'),
            *_chars('abc\ndef'),
            ESCAPE_KEY,
            _csi('[201~', 'CSI'),
            BACKSPACE_KEY,
            BACKSPACE_KEY,
            ESCAPE_KEY,
            ESCAPE_KEY,
        ]

        result = _run_prompt(keys)

        self.assertIsNone(result)
        self.assertEqual(tui._buffer, [])

    def test_backspace_after_typing_past_a_paste_only_removes_the_typed_char(self) -> None:
        keys = [
            ESCAPE_KEY,
            _csi('[200~', 'CSI'),
            *_chars('abc\ndef'),
            ESCAPE_KEY,
            _csi('[201~', 'CSI'),
            *_chars('xy'),
            BACKSPACE_KEY,
            ENTER_KEY,
        ]

        result = _run_prompt(keys)

        self.assertEqual(result, 'abc\ndefx')

    def test_paste_after_typed_text_appends_to_the_buffer(self) -> None:
        keys = [
            *_chars('explain '),
            ESCAPE_KEY,
            _csi('[200~', 'CSI'),
            *_chars('this code\nprint(1)'),
            ESCAPE_KEY,
            _csi('[201~', 'CSI'),
            ENTER_KEY,
        ]

        result = _run_prompt(keys)

        self.assertEqual(result, 'explain this code\nprint(1)')
