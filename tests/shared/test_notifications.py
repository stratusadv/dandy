import subprocess
from unittest import TestCase, mock

from dandy.shared.notifications import os_desktop_notify


class TestOsDesktopNotify(TestCase):
    def setUp(self) -> None:
        import dandy.shared.notifications as module

        patch = mock.patch.object(module, '_flags', {})
        patch.start()
        self.addCleanup(patch.stop)

    def test_linux_spawns_notify_send(self) -> None:
        with (
            mock.patch('dandy.shared.notifications.sys') as mock_sys,
            mock.patch('subprocess.Popen') as mock_popen,
        ):
            mock_sys.platform = 'linux'
            os_desktop_notify('Request completed')

        mock_popen.assert_called_once_with(
            ['notify-send', '--urgency=low', 'Dandy', 'Request completed'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def test_macos_spawns_osascript_with_an_escaped_message(self) -> None:
        with (
            mock.patch('dandy.shared.notifications.sys') as mock_sys,
            mock.patch('subprocess.Popen') as mock_popen,
        ):
            mock_sys.platform = 'darwin'
            os_desktop_notify('Say "hi" now')

        command = mock_popen.call_args.args[0]
        script = command[2]

        self.assertEqual(command[0], 'osascript')
        self.assertEqual(command[1], '-e')
        self.assertIn('display notification', script)
        self.assertIn('with title "Dandy"', script)
        self.assertIn('Say \\"hi\\" now', script)

    def test_other_platforms_are_a_noop(self) -> None:
        with (
            mock.patch('dandy.shared.notifications.sys') as mock_sys,
            mock.patch('subprocess.Popen') as mock_popen,
        ):
            mock_sys.platform = 'win32'
            os_desktop_notify('Request completed')

        mock_popen.assert_not_called()

    def test_missing_binary_is_cached(self) -> None:
        import dandy.shared.notifications as module

        with (
            mock.patch('dandy.shared.notifications.sys') as mock_sys,
            mock.patch('subprocess.Popen', side_effect=FileNotFoundError('no notify-send')),
        ):
            mock_sys.platform = 'linux'
            os_desktop_notify('Request completed')
            self.assertTrue(module._flags.get('missing'))

            with mock.patch('subprocess.Popen') as mock_popen_cached:
                os_desktop_notify('Again')
                mock_popen_cached.assert_not_called()

    def test_spawn_failure_never_raises(self) -> None:
        with (
            mock.patch('dandy.shared.notifications.sys') as mock_sys,
            mock.patch('subprocess.Popen', side_effect=OSError('spawn failed')),
        ):
            mock_sys.platform = 'linux'
            os_desktop_notify('Request completed')
