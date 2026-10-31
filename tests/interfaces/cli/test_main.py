import runpy
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase, mock

import dandy.interfaces.cli.main as cli_main
from dandy.shared.settings import settings
from dandy.shared.constants import __VERSION__


class TestCliMain(TestCase):
    def test_help_prints_usage_and_skips_settings(self) -> None:
        with (
            mock.patch.object(cli_main, 'check_or_create_settings') as mock_check_settings,
            mock.patch.object(sys, 'argv', ['dandy', '-h']),
            redirect_stdout(StringIO()) as out,
        ):
            cli_main.main()

        self.assertIn('Usage:', out.getvalue())
        self.assertIn('dandy "<your request>"', out.getvalue())
        mock_check_settings.assert_not_called()

    def test_version_prints_version_and_skips_settings(self) -> None:
        with (
            mock.patch.object(cli_main, 'check_or_create_settings') as mock_check_settings,
            mock.patch.object(sys, 'argv', ['dandy', '--version']),
            redirect_stdout(StringIO()) as out,
        ):
            cli_main.main()

        self.assertIn(__VERSION__, out.getvalue())
        mock_check_settings.assert_not_called()

    def test_script_entry_exits_with_main_return_code(self) -> None:
        main_path = Path(cli_main.__file__)

        with (
            mock.patch.object(sys, 'argv', ['dandy', '-h']),
            redirect_stdout(StringIO()) as out,
            self.assertRaises(SystemExit) as context,
        ):
            runpy.run_path(str(main_path), run_name='__main__')

        self.assertIn('Usage:', out.getvalue())
        self.assertIn(context.exception.code, (None, 0))

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_one_shot_mode_processes_a_single_request(
        self,
        mock_reload: mock.MagicMock,
        mock_check_settings: mock.MagicMock,
        mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_session.is_loaded = False

        with (
            mock.patch.object(sys, 'argv', ['dandy', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()),
        ):
            cli_main.main()

        mock_check_settings.assert_called_once_with(cli_main.CWD_PATH)
        mock_reload.assert_called_once()
        mock_session.post_init.assert_called_once_with(project_base_path=cli_main.CWD_PATH)
        mock_session.load.assert_called_once()
        mock_session.save.assert_called_once()

        cli_instance = mock_cli_class.return_value
        cli_instance.process_user_input.assert_called_once_with(user_input='do the thing')
        cli_instance.run.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_no_args_starts_the_repl(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_session.is_loaded = True

        with mock.patch.object(sys, 'argv', ['dandy']), redirect_stdout(StringIO()):
            cli_main.main()

        mock_session.save.assert_not_called()
        mock_cli_class.return_value.run.assert_called_once()
        mock_cli_class.return_value.process_user_input.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_loaded_session_is_not_saved_again(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        mock_session: mock.MagicMock,
        _mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_session.is_loaded = True

        with mock.patch.object(sys, 'argv', ['dandy', 'request']), redirect_stdout(StringIO()):
            cli_main.main()

        mock_session.load.assert_called_once()
        mock_session.save.assert_not_called()
