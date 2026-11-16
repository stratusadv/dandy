from unittest import TestCase, mock

from dandy.interfaces.cli.tui.notify import (
    NOTIFICATION_MAX_LENGTH,
    desktop_notify,
    notification_sequences,
    notification_text,
)


class TestNotificationText(TestCase):
    def test_single_line_text_is_unchanged(self) -> None:
        text = 'Request Completed in 4.2 seconds'

        self.assertEqual(notification_text(text), text)

    def test_whitespace_runs_fold_to_single_spaces(self) -> None:
        self.assertEqual(notification_text('  Which   color?\n'), 'Which color?')

    def test_long_text_is_capped_with_an_ellipsis(self) -> None:
        text = notification_text('x' * (NOTIFICATION_MAX_LENGTH + 10))

        self.assertEqual(len(text), NOTIFICATION_MAX_LENGTH)
        self.assertTrue(text.endswith('…'))

    def test_exact_length_text_is_untouched(self) -> None:
        text = 'y' * NOTIFICATION_MAX_LENGTH

        self.assertEqual(notification_text(text), text)

    def test_empty_text_stays_empty(self) -> None:
        self.assertEqual(notification_text('   \n  '), '')


class TestNotificationSequences(TestCase):
    def test_sequences_carry_osc_777_and_osc_9_with_bell_terminators(self) -> None:
        sequences = notification_sequences('Which color?')
        expected = '\x1b]777;notify\x07Dandy\x07Which color?\x07\x1b]9;Which color?\x07'

        self.assertEqual(sequences, expected)

    def test_sequences_collapse_and_cap_the_message(self) -> None:
        sequences = notification_sequences(f'a  b\n{"z" * 200}')

        self.assertEqual(sequences.count('\x07'), 4)
        self.assertIn('a b ' + 'z' * (NOTIFICATION_MAX_LENGTH - 5) + '…', sequences)
        self.assertNotIn('\n', sequences)


class TestDesktopNotify(TestCase):
    @mock.patch('sys.stdout.write')
    def test_writes_the_sequences_and_flushes(self, mock_write: mock.MagicMock) -> None:
        with mock.patch('sys.stdout.flush') as mock_flush:
            desktop_notify('Which color?')

        mock_write.assert_called_once_with(
            '\x1b]777;notify\x07Dandy\x07Which color?\x07\x1b]9;Which color?\x07'
        )
        mock_flush.assert_called_once()

    @mock.patch('sys.stdout.write', side_effect=OSError('no tty'))
    def test_survives_unwritable_stdout(self, mock_write: mock.MagicMock) -> None:
        desktop_notify('Which color?')

    @mock.patch('sys.stdout.flush', side_effect=OSError('no tty'))
    def test_survives_unflushable_stdout(self, mock_flush: mock.MagicMock) -> None:
        with mock.patch('sys.stdout.write'):
            desktop_notify('Which color?')
