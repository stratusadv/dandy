import runpy
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase, mock

import dandy.interfaces.cli.main as cli_main
from dandy.interfaces.cli.one_shot import OneShotPlan, parse_one_shot
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
        self.assertIn('dandy --continue "<request>"', out.getvalue())
        self.assertIn('dandy --init', out.getvalue())
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
        with (
            mock.patch.object(sys, 'argv', ['dandy', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()),
        ):
            cli_main.main()

        mock_check_settings.assert_called_once_with(cli_main.CWD_PATH)
        mock_reload.assert_called_once()
        mock_session.post_init.assert_called_once_with(project_base_path=cli_main.CWD_PATH)

        cli_instance = mock_cli_class.return_value
        cli_instance.process_user_input.assert_called_once_with(user_input='do the thing')
        cli_instance.continue_latest_session.assert_not_called()
        cli_instance.run.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_no_args_starts_the_repl(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with mock.patch.object(sys, 'argv', ['dandy']), redirect_stdout(StringIO()):
            cli_main.main()

        mock_cli_class.return_value.run.assert_called_once()
        mock_cli_class.return_value.process_user_input.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_one_shot_continue_runs_in_the_latest_session(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with (
            mock.patch.object(sys, 'argv', ['dandy', '--continue', 'keep', 'going']),
            redirect_stdout(StringIO()),
        ):
            cli_main.main()

        cli_instance = mock_cli_class.return_value
        cli_instance.continue_latest_session.assert_called_once_with('keep going')
        cli_instance.process_user_input.assert_not_called()
        cli_instance.run.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_one_shot_mode_exits_zero_when_the_turn_succeeds(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.last_turn_succeeded = True

        with (
            mock.patch.object(sys, 'argv', ['dandy', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_one_shot_mode_exits_nonzero_when_the_turn_fails(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.last_turn_succeeded = False

        with (
            mock.patch.object(sys, 'argv', ['dandy', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 1)

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_continue_mode_exits_with_the_turn_outcome(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        cli_instance = mock_cli_class.return_value
        cli_instance.continue_latest_session.return_value = True

        with (
            mock.patch.object(sys, 'argv', ['dandy', '--continue', 'keep', 'going']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

        cli_instance.continue_latest_session.return_value = False

        with (
            mock.patch.object(sys, 'argv', ['dandy', '--continue', 'keep', 'going']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 1)

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_one_shot_init_runs_the_init_pass(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.run_init.return_value = True

        with mock.patch.object(sys, 'argv', ['dandy', '--init']), redirect_stdout(StringIO()):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

        cli_instance = mock_cli_class.return_value
        cli_instance.run_init.assert_called_once_with()
        cli_instance.process_user_input.assert_not_called()
        cli_instance.continue_latest_session.assert_not_called()
        cli_instance.run.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_one_shot_init_exits_nonzero_when_the_pass_fails(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.run_init.return_value = False

        with mock.patch.object(sys, 'argv', ['dandy', '--init']), redirect_stdout(StringIO()):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 1)

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    def test_one_shot_init_with_a_request_prints_usage(
        self,
        mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with (
            mock.patch.object(sys, 'argv', ['dandy', '--init', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()) as out,
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)
        self.assertIn('Usage:', out.getvalue())
        mock_check_settings.assert_not_called()
        mock_cli_class.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    def test_bare_continue_flag_prints_usage(
        self,
        mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with (
            mock.patch.object(sys, 'argv', ['dandy', '--continue']),
            redirect_stdout(StringIO()) as out,
        ):
            cli_main.main()

        self.assertIn('Usage:', out.getvalue())
        mock_check_settings.assert_not_called()
        mock_cli_class.assert_not_called()


class TestParseOneShot(TestCase):
    def test_bare_call_is_the_repl(self) -> None:
        self.assertEqual(parse_one_shot([]), OneShotPlan(repl=True))

    def test_plain_request_joins_the_tokens(self) -> None:
        plan = parse_one_shot(['do', 'the', 'thing'])

        self.assertEqual(plan.request, 'do the thing')
        self.assertFalse(plan.repl)
        self.assertIsNone(plan.command)

    def test_unknown_dash_tokens_stay_in_the_request(self) -> None:
        plan = parse_one_shot(['--weird', 'hi'])

        self.assertEqual(plan.request, '--weird hi')
        self.assertIsNone(plan.command)

    def test_quit_flag_is_not_a_flag(self) -> None:
        plan = parse_one_shot(['-q'])

        self.assertEqual(plan.request, '-q')
        self.assertIsNone(plan.command)

    def test_continue_needs_a_request(self) -> None:
        self.assertIsNone(parse_one_shot(['--continue']))

        plan = parse_one_shot(['--continue', 'keep', 'going'])

        self.assertTrue(plan.continue_latest)
        self.assertEqual(plan.request, 'keep going')

    def test_init_flag_stands_alone(self) -> None:
        self.assertEqual(parse_one_shot(['-i']).command, 'init')
        self.assertEqual(parse_one_shot(['--init']).command, 'init')
        self.assertIsNone(parse_one_shot(['--init', 'do', 'it']))

    def test_sessions_flag_without_name_lists(self) -> None:
        for tokens in (['-s'], ['--sessions']):
            plan = parse_one_shot(tokens)

            self.assertEqual(plan.command, 'sessions')
            self.assertIsNone(plan.name)
            self.assertFalse(plan.repl)

    def test_sessions_flag_with_name_and_no_request_is_a_repl_resume(self) -> None:
        plan = parse_one_shot(['-s', 'my-session'])

        self.assertEqual(plan.command, 'sessions')
        self.assertEqual(plan.name, 'my-session')
        self.assertTrue(plan.repl)

    def test_sessions_flag_with_name_and_request_runs_a_turn(self) -> None:
        plan = parse_one_shot(['--sessions', 'my-session', 'do', 'it'])

        self.assertEqual(plan.command, 'sessions')
        self.assertEqual(plan.name, 'my-session')
        self.assertEqual(plan.request, 'do it')
        self.assertFalse(plan.repl)

    def test_resume_flag_requires_a_name(self) -> None:
        self.assertIsNone(parse_one_shot(['-r']))
        self.assertIsNone(parse_one_shot(['--resume', '--continue']))

    def test_resume_flag_with_name_only_is_a_repl_resume(self) -> None:
        plan = parse_one_shot(['--resume', 'my-session'])

        self.assertEqual(plan.command, 'resume')
        self.assertEqual(plan.name, 'my-session')
        self.assertTrue(plan.repl)

    def test_resume_flag_with_name_and_request_runs_a_turn(self) -> None:
        plan = parse_one_shot(['-r', 'my-session', 'do', 'it'])

        self.assertEqual(plan.command, 'resume')
        self.assertEqual(plan.name, 'my-session')
        self.assertEqual(plan.request, 'do it')
        self.assertFalse(plan.repl)

    def test_delete_flag_requires_a_name_and_no_request(self) -> None:
        self.assertIsNone(parse_one_shot(['-d']))

        plan = parse_one_shot(['--delete', 'my-session'])

        self.assertEqual(plan.command, 'delete')
        self.assertEqual(plan.name, 'my-session')

        self.assertIsNone(parse_one_shot(['-d', 'my-session', 'do', 'it']))

    def test_new_flag_forms(self) -> None:
        plan = parse_one_shot(['-n'])

        self.assertEqual(plan.command, 'new')
        self.assertTrue(plan.repl)
        self.assertIsNone(plan.name)

        plan = parse_one_shot(['-n', 'my-session'])

        self.assertTrue(plan.repl)
        self.assertEqual(plan.name, 'my-session')

        plan = parse_one_shot(['--new', 'my-session', 'do', 'it'])

        self.assertFalse(plan.repl)
        self.assertEqual(plan.name, 'my-session')
        self.assertEqual(plan.request, 'do it')

    def test_conflicting_action_flags_print_usage(self) -> None:
        self.assertIsNone(parse_one_shot(['-s', 'x', '-r', 'y']))
        self.assertIsNone(parse_one_shot(['--continue', 'x', '--init']))
        self.assertIsNone(parse_one_shot(['-s', '--continue', 'x']))
        self.assertIsNone(parse_one_shot(['-s', 'x', '-s', 'y']))


class TestOneShotCommandFlags(TestCase):
    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_sessions_flag_lists_and_exits_zero(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with mock.patch.object(sys, 'argv', ['dandy', '--sessions']), redirect_stdout(StringIO()):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

        cli_instance = mock_cli_class.return_value
        cli_instance.run_sessions_list.assert_called_once_with()
        cli_instance.run.assert_not_called()
        cli_instance.process_user_input.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_sessions_short_flag_with_name_opens_the_repl_on_that_session(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.load_named_session.return_value = True

        with (
            mock.patch.object(sys, 'argv', ['dandy', '-s', 'my-session']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

        cli_instance = mock_cli_class.return_value
        cli_instance.load_named_session.assert_called_once_with('my-session')
        cli_instance.run.assert_called_once_with()
        cli_instance.process_user_input.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_sessions_short_flag_with_unknown_name_exits_nonzero(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.load_named_session.return_value = False

        with (
            mock.patch.object(sys, 'argv', ['dandy', '-s', 'no-such-session']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 1)
        mock_cli_class.return_value.run.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_sessions_flag_with_name_and_request_runs_one_turn_in_it(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.run_in_session.return_value = True

        with (
            mock.patch.object(sys, 'argv', ['dandy', '-s', 'my-session', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

        cli_instance = mock_cli_class.return_value
        cli_instance.run_in_session.assert_called_once_with('my-session', 'do the thing')
        cli_instance.run.assert_not_called()
        cli_instance.process_user_input.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_resume_flag_with_name_and_request_runs_one_turn_in_it(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.run_in_session.return_value = False

        with (
            mock.patch.object(sys, 'argv', ['dandy', '-r', 'my-session', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 1)

        cli_instance = mock_cli_class.return_value
        cli_instance.run_in_session.assert_called_once_with('my-session', 'do the thing')

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_delete_flag_removes_the_session(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.run_delete.return_value = True

        with (
            mock.patch.object(sys, 'argv', ['dandy', '--delete', 'my-session']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

        cli_instance = mock_cli_class.return_value
        cli_instance.run_delete.assert_called_once_with('my-session')
        cli_instance.run.assert_not_called()
        cli_instance.process_user_input.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_new_flag_with_name_and_request_starts_a_fresh_conversation(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.run_new_one_shot.return_value = True

        with (
            mock.patch.object(sys, 'argv', ['dandy', '-n', 'my-session', 'do', 'the', 'thing']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)

        cli_instance = mock_cli_class.return_value
        cli_instance.run_new_one_shot.assert_called_once_with('my-session', 'do the thing')
        cli_instance.run.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_new_flag_with_name_and_no_request_opens_a_pre_named_repl(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with (
            mock.patch.object(sys, 'argv', ['dandy', '-n', 'my-session']),
            redirect_stdout(StringIO()),
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)
        mock_cli_class.return_value.run.assert_called_once_with(new_name='my-session')

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_init_short_flag_runs_the_init_pass(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        mock_cli_class.return_value.run_init.return_value = True

        with mock.patch.object(sys, 'argv', ['dandy', '-i']), redirect_stdout(StringIO()):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)
        mock_cli_class.return_value.run_init.assert_called_once_with()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    @mock.patch.object(settings, 'reload_from_os')
    def test_slash_form_one_shot_still_reaches_process_user_input(
        self,
        _mock_reload: mock.MagicMock,
        _mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with mock.patch.object(sys, 'argv', ['dandy', '/sessions']), redirect_stdout(StringIO()):
            cli_main.main()

        mock_cli_class.return_value.process_user_input.assert_called_once_with(
            user_input='/sessions'
        )
        mock_cli_class.return_value.run_sessions_list.assert_not_called()

    @mock.patch('dandy.interfaces.cli.cli.DandyCli')
    @mock.patch.object(cli_main, 'session')
    @mock.patch.object(cli_main, 'check_or_create_settings')
    def test_conflicting_flags_print_usage(
        self,
        mock_check_settings: mock.MagicMock,
        _mock_session: mock.MagicMock,
        mock_cli_class: mock.MagicMock,
    ) -> None:
        with (
            mock.patch.object(sys, 'argv', ['dandy', '-s', 'x', '-r', 'y']),
            redirect_stdout(StringIO()) as out,
        ):
            exit_code = cli_main.main()

        self.assertEqual(exit_code, 0)
        self.assertIn('Usage:', out.getvalue())
        mock_check_settings.assert_not_called()
        mock_cli_class.assert_not_called()
