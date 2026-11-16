import os
import types
from pathlib import Path
from unittest import TestCase, mock

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.interfaces.cli.tui.notify import (
    NOTIFICATION_MAX_LENGTH,
    PROBE_QUERY,
    _terminal_supports_notifications,
    desktop_notify,
    notification_sequences,
    notification_text,
    notifications_enabled,
)

OSC9_ONLY = '\x1b]9;Which color?\x07'


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
    def test_sequence_is_osc_9_with_a_bell_terminator(self) -> None:
        sequences = notification_sequences('Which color?')

        self.assertEqual(sequences, OSC9_ONLY)

    def test_sequence_never_carries_osc_777(self) -> None:
        self.assertNotIn('777', notification_sequences('Which color?'))

    def test_sequences_collapse_and_cap_the_message(self) -> None:
        sequences = notification_sequences(f'a  b\n{"z" * 200}')

        self.assertEqual(sequences.count('\x07'), 1)
        self.assertIn('a b ' + 'z' * (NOTIFICATION_MAX_LENGTH - 5) + '…', sequences)
        self.assertNotIn('\n', sequences)


class TestNotificationsEnabled(TestCase):
    def setUp(self) -> None:
        env_patch = mock.patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _setting_enabled(self, enabled: bool) -> None:
        setting_patch = mock.patch(
            'dandy.interfaces.cli.tui.notify.settings',
            create=True,
            new=mock.MagicMock(DESKTOP_NOTIFICATIONS=enabled),
        )
        setting_patch.start()
        self.addCleanup(setting_patch.stop)

    def test_setting_false_disables(self) -> None:
        self._setting_enabled(False)

        self.assertFalse(notifications_enabled())

    def test_setting_true_enables(self) -> None:
        self._setting_enabled(True)

        self.assertTrue(notifications_enabled())

    def test_setting_missing_defaults_on(self) -> None:
        with mock.patch(
            'dandy.interfaces.cli.tui.notify.settings', new=types.SimpleNamespace(), create=True
        ):
            self.assertTrue(notifications_enabled())

    def test_env_override_on_enables_even_with_setting_false(self) -> None:
        self._setting_enabled(False)
        os.environ['DANDY_DESKTOP_NOTIFICATIONS'] = '1'

        self.assertTrue(notifications_enabled())

    def test_env_override_off_disables_even_with_setting_true(self) -> None:
        self._setting_enabled(True)
        os.environ['DANDY_DESKTOP_NOTIFICATIONS'] = '0'

        self.assertFalse(notifications_enabled())


class TestTerminalSupportProbe(TestCase):
    def setUp(self) -> None:
        self.notify_module = mock.patch('dandy.interfaces.cli.tui.notify._support', {})
        self.notify_module.start()
        self.addCleanup(self.notify_module.stop)

        self.term = Terminal()

        self.stdout_patch = mock.patch('sys.stdout.write')
        self.mock_write = self.stdout_patch.start()
        self.addCleanup(self.stdout_patch.stop)

        self.flush_patch = mock.patch('sys.stdout.flush')
        self.mock_flush = self.flush_patch.start()
        self.addCleanup(self.flush_patch.stop)

        self.cbreak_patch = mock.patch.object(self.term, 'cbreak')
        self.cbreak_patch.start()
        self.addCleanup(self.cbreak_patch.stop)

    def _written(self) -> list[str]:
        return [str(call.args[0]) for call in self.mock_write.call_args_list if call.args]

    def test_terminal_answering_yes_supports_notifications(self) -> None:
        reply = Keystroke('\x1b[?633;1C')

        with mock.patch.object(
            self.term, 'inkey', side_effect=[Keystroke(''), reply]
        ) as mock_inkey:
            self.assertTrue(_terminal_supports_notifications(self.term))

        written = ''.join(self._written())
        self.assertIn(PROBE_QUERY, written)
        self.assertTrue(mock_inkey.call_args.kwargs['timeout'] < 0.1)

    def test_terminal_answering_no_does_not_support_notifications(self) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=[Keystroke('\x1b[?633;0C')]):
            self.assertFalse(_terminal_supports_notifications(self.term))

    def test_unanswered_terminal_does_not_support_notifications(self) -> None:
        with (
            mock.patch.object(self.term, 'inkey', return_value=Keystroke('')),
            mock.patch('dandy.interfaces.cli.tui.notify.time') as mock_time,
        ):
            # The clock jumps past the probe deadline after the first poll.
            mock_time.perf_counter.side_effect = [0.0, 10.0]
            self.assertFalse(_terminal_supports_notifications(self.term))

    def test_unreadable_input_does_not_support_notifications(self) -> None:
        with mock.patch.object(self.term, 'inkey', side_effect=OSError('no tty')):
            self.assertFalse(_terminal_supports_notifications(self.term))

    def test_probe_result_is_cached(self) -> None:
        with mock.patch.object(
            self.term, 'inkey', side_effect=[Keystroke(''), Keystroke('\x1b[?633;1C')]
        ) as mock_inkey:
            self.assertTrue(_terminal_supports_notifications(self.term))
            self.assertTrue(_terminal_supports_notifications(self.term))

        self.assertEqual(mock_inkey.call_count, 2)


class TestDesktopNotify(TestCase):
    def setUp(self) -> None:
        self.os_notify = mock.patch('dandy.interfaces.cli.tui.notify.os_desktop_notify')
        self.mock_os_notify = self.os_notify.start()
        self.addCleanup(self.os_notify.stop)

        self.session = mock.patch(
            'dandy.interfaces.cli.tui.notify.session',
            new=types.SimpleNamespace(project_base_path=Path('/proj')),
        )
        self.session.start()
        self.addCleanup(self.session.stop)

    def test_supported_terminal_writes_osc9_only(self) -> None:
        with (
            mock.patch('dandy.interfaces.cli.tui.notify.notifications_enabled', return_value=True),
            mock.patch(
                'dandy.interfaces.cli.tui.notify._terminal_supports_notifications',
                return_value=True,
            ),
            mock.patch('sys.stdout.write') as mock_write,
            mock.patch('sys.stdout.flush') as mock_flush,
        ):
            desktop_notify('Which color?', Terminal())

        mock_write.assert_called_once_with('\x1b]9;proj — Which color?\x07')
        mock_flush.assert_called_once()
        self.mock_os_notify.assert_not_called()

    def test_unanswered_terminal_falls_back_to_the_os(self) -> None:
        with (
            mock.patch('dandy.interfaces.cli.tui.notify.notifications_enabled', return_value=True),
            mock.patch(
                'dandy.interfaces.cli.tui.notify._terminal_supports_notifications',
                return_value=False,
            ),
            mock.patch('sys.stdout.write') as mock_write,
        ):
            desktop_notify('Which color?', Terminal())

        written = ''.join(str(call.args[0]) for call in mock_write.call_args_list if call.args)
        self.assertNotIn('\x1b]9;', written)
        self.mock_os_notify.assert_called_once_with('proj — Which color?')

    def test_empty_project_name_drops_the_prefix(self) -> None:
        with mock.patch(
            'dandy.interfaces.cli.tui.notify.session',
            new=types.SimpleNamespace(project_base_path=Path('/')),
        ):
            with (
                mock.patch(
                    'dandy.interfaces.cli.tui.notify._terminal_supports_notifications',
                    return_value=False,
                ),
                mock.patch('sys.stdout.write'),
            ):
                desktop_notify('Which color?', Terminal())

        self.mock_os_notify.assert_called_once_with('Which color?')

    def test_skips_silently_when_disabled(self) -> None:
        with (
            mock.patch('dandy.interfaces.cli.tui.notify.notifications_enabled', return_value=False),
            mock.patch('sys.stdout.write') as mock_write,
        ):
            desktop_notify('Which color?', Terminal())

        mock_write.assert_not_called()
        self.mock_os_notify.assert_not_called()

    def test_unwritable_stdout_falls_back_to_the_os(self) -> None:
        with (
            mock.patch('dandy.interfaces.cli.tui.notify.notifications_enabled', return_value=True),
            mock.patch(
                'dandy.interfaces.cli.tui.notify._terminal_supports_notifications',
                return_value=True,
            ),
            mock.patch('sys.stdout.write', side_effect=OSError('no tty')),
        ):
            desktop_notify('Which color?', Terminal())

        self.mock_os_notify.assert_called_once_with('proj — Which color?')

    def test_unflushable_stdout_falls_back_to_the_os(self) -> None:
        with (
            mock.patch('dandy.interfaces.cli.tui.notify.notifications_enabled', return_value=True),
            mock.patch(
                'dandy.interfaces.cli.tui.notify._terminal_supports_notifications',
                return_value=True,
            ),
            mock.patch('sys.stdout.write'),
            mock.patch('sys.stdout.flush', side_effect=OSError('no tty')),
        ):
            desktop_notify('Which color?', Terminal())

        self.mock_os_notify.assert_called_once_with('proj — Which color?')
