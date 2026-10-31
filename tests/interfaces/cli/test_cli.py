import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from dandy.application.agent.intel import AgentSession
from dandy.application.agent.session import session
from dandy.application.agent.session_store import SessionStore
from dandy.interfaces.cli.cli import DandyCli
from dandy.interfaces.cli.tui.printer import session_banner_line
from dandy.interfaces.cli.tui.tui import tui
from dandy.shared.settings import settings


def _make_agent_session(last_request: str) -> AgentSession:
    return AgentSession(last_request=last_request)


class TestDandyCli(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

        with mock.patch.object(tui.printer, 'welcome'):
            self.cli = DandyCli()

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def _run_turn_with_history(self, user_input: str, mock_turn: mock.MagicMock) -> None:
        self.cli.agent.last_request = user_input
        self.cli.agent.history.add_message(role='user', text=user_input)
        self.cli.agent.history.add_message(role='assistant', text='Done.')

        mock_turn.return_value = mock.MagicMock(text='answer')
        self.cli.process_user_input(user_input)

    @mock.patch.object(tui, 'get_user_input', return_value=None)
    def test_run_exits_when_escape_pressed_twice(self, mock_get_user_input: mock.MagicMock) -> None:
        self.cli.run()

        mock_get_user_input.assert_called_once_with()

    @mock.patch.object(tui, 'get_user_input', return_value='/quit')
    def test_run_exits_on_quit_command(self, mock_get_user_input: mock.MagicMock) -> None:
        self.cli.run()

        mock_get_user_input.assert_called_once_with()

    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    @mock.patch.object(tui.printer, 'green_divider')
    @mock.patch.object(tui.printer, 'output')
    def test_process_user_input_sends_plain_text_to_agent(
        self,
        mock_output: mock.MagicMock,
        mock_green_divider: mock.MagicMock,
        mock_turn: mock.MagicMock,
    ) -> None:
        mock_turn.return_value = mock.MagicMock(text='answer')

        should_continue = self.cli.process_user_input('hello there')

        self.assertTrue(should_continue)
        mock_turn.assert_called_once()
        mock_green_divider.assert_called_once_with()
        mock_output.assert_called_once_with('answer')

    @mock.patch(
        'dandy.application.agent.coding_agent.CodingAgent.turn', side_effect=RuntimeError('boom')
    )
    @mock.patch.object(tui.printer, 'error')
    def test_process_agent_input_reports_error_on_failure(
        self, mock_error: mock.MagicMock, _mock_turn: mock.MagicMock
    ) -> None:
        should_continue = self.cli.process_user_input('do something')

        self.assertTrue(should_continue)
        mock_error.assert_called_once_with(error='Coding agent failed', description='boom')

    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    @mock.patch.object(tui.printer, 'green_divider')
    @mock.patch.object(tui.printer, 'output')
    def test_process_agent_input_passes_verbose_callback_when_debug_is_on(
        self,
        _mock_output: mock.MagicMock,
        _mock_green_divider: mock.MagicMock,
        mock_turn: mock.MagicMock,
    ) -> None:
        with mock.patch.object(settings, 'DEBUG', new=True):
            self.cli = DandyCli()

        self.cli.process_agent_input('do something')

        _, kwargs = mock_turn.call_args
        verbose_callback = kwargs.get('verbose_callback')

        self.assertIsNotNone(verbose_callback)

        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            verbose_callback('Round 1: model requested 1 tool call(s)')

        self.assertIn('Round 1: model requested 1 tool call(s)', buffer.getvalue())

    def test_verbose_callback_is_none_when_debug_is_off(self) -> None:
        with mock.patch.object(settings, 'DEBUG', new=False):
            self.cli = DandyCli()

        self.assertIsNone(self.cli.verbose_callback)

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_turn_without_history_saves_no_session(
        self, mock_turn: mock.MagicMock, _mock_output: mock.MagicMock
    ) -> None:
        mock_turn.return_value = mock.MagicMock(text='answer')

        self.cli.process_user_input('hello there')

        self.assertIsNone(self.cli.active_name)
        self.assertEqual(self.cli.session_store.list_sessions(), [])

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_first_turn_auto_saves_a_named_session(
        self, mock_turn: mock.MagicMock, _mock_output: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)

        self.assertIsNotNone(self.cli.active_name)
        self.assertTrue(self.cli.active_name.startswith('2026-'))
        self.assertTrue(self.cli.session_store._record_path(self.cli.active_name).is_file())

        loaded = self.cli.session_store.load(self.cli.active_name)
        self.assertEqual(loaded.last_request, 'Fix the login bug')
        self.assertEqual(len(loaded.messages), 2)

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_later_turns_update_the_same_session(
        self, mock_turn: mock.MagicMock, _mock_output: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)
        first_name = self.cli.active_name

        self._run_turn_with_history('Now fix the tests too', mock_turn)

        self.assertEqual(self.cli.active_name, first_name)
        self.assertEqual(
            self.cli.session_store.load(first_name).last_request, 'Now fix the tests too'
        )

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_stateless_turn_saves_no_session(
        self, mock_turn: mock.MagicMock, _mock_output: mock.MagicMock
    ) -> None:
        self.cli.agent.history.add_message(role='user', text='hello there')
        mock_turn.return_value = mock.MagicMock(text='answer')

        self.cli.process_user_input('hello there', save_session=False)

        self.assertIsNone(self.cli.active_name)
        self.assertEqual(self.cli.session_store.list_sessions(), [])

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_continue_latest_session_runs_turn_and_resaves(
        self, mock_turn: mock.MagicMock, mock_output: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)
        saved_name = self.cli.active_name

        mock_turn.return_value = mock.MagicMock(text='answer')

        self.cli.continue_latest_session('And the database one too')

        self.assertEqual(self.cli.active_name, saved_name)
        self.assertEqual(mock_turn.call_args[0][0], 'And the database one too')
        self.assertEqual(self.cli.session_store.load(saved_name).last_request, 'Fix the login bug')
        self.assertIn(
            f'Saved session "{saved_name}" (2 messages).', mock_output.call_args_list[-1][0][0]
        )

    @mock.patch.object(tui.printer, 'error')
    def test_continue_latest_session_without_sessions_reports_error(
        self, mock_error: mock.MagicMock
    ) -> None:
        self.cli.continue_latest_session('Do something')

        mock_error.assert_called_once_with(
            error='No session to continue',
            description='There are no saved sessions for this project yet.',
        )

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_new_command_starts_fresh_conversation(
        self, mock_turn: mock.MagicMock, mock_output: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)

        should_continue = self.cli.process_user_input('/new')

        self.assertTrue(should_continue)
        self.assertIsNone(self.cli.active_name)
        self.assertEqual(len(self.cli.agent.history), 0)
        self.assertIn('new conversation', mock_output.call_args[0][0])

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_new_command_with_name_pre_names_the_session(
        self, mock_turn: mock.MagicMock, mock_output: mock.MagicMock
    ) -> None:
        self.cli.process_user_input('/new my work')

        self.assertEqual(self.cli.active_name, 'my work')
        self.assertIn('my work', mock_output.call_args[0][0])

        self._run_turn_with_history('Fix the login bug', mock_turn)

        self.assertTrue(self.cli.session_store._record_path('my work').is_file())

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_sessions_command_lists_saved_sessions(
        self, mock_turn: mock.MagicMock, mock_output: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)

        self.cli.process_user_input('/sessions')

        table = mock_output.call_args[0][0]
        self.assertIn('**' + self.cli.active_name + '**', table)
        self.assertIn('Messages', table)

    @mock.patch.object(tui.printer, 'output')
    def test_sessions_command_reports_empty_state(self, mock_output: mock.MagicMock) -> None:
        self.cli.process_user_input('/sessions')

        self.assertIn('No sessions', mock_output.call_args[0][0])

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_resume_command_loads_the_session(
        self, mock_turn: mock.MagicMock, mock_output: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)
        saved_name = self.cli.active_name

        self.cli.agent.clear()

        with mock.patch.object(self.cli.agent, 'load_session') as mock_load_session:
            self.cli.process_user_input(f'/resume {saved_name}')

        self.assertEqual(self.cli.active_name, saved_name)

        loaded_session = mock_load_session.call_args[0][0]
        self.assertEqual(loaded_session.last_request, 'Fix the login bug')
        self.assertIn('Resumed session', mock_output.call_args[0][0])

    @mock.patch.object(tui.printer, 'error')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_resume_unknown_session_lists_available(
        self, mock_turn: mock.MagicMock, mock_error: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)
        active_name = self.cli.active_name

        self.cli.process_user_input('/resume does-not-exist')

        self.assertEqual(self.cli.active_name, active_name)
        description = mock_error.call_args.kwargs['description']
        self.assertIn('does-not-exist', description)
        self.assertIn(self.cli.session_store.latest(), description)

    @mock.patch.object(tui.printer, 'error')
    def test_resume_without_name_reports_usage(self, mock_error: mock.MagicMock) -> None:
        self.cli.process_user_input('/resume')

        mock_error.assert_called_once_with(error='Usage', description='/resume <name>')

    @mock.patch.object(tui.printer, 'output')
    @mock.patch('dandy.application.agent.coding_agent.CodingAgent.turn')
    def test_delete_command_removes_and_unbinds_active_session(
        self, mock_turn: mock.MagicMock, mock_output: mock.MagicMock
    ) -> None:
        self._run_turn_with_history('Fix the login bug', mock_turn)
        saved_name = self.cli.active_name

        self.cli.process_user_input(f'/delete {saved_name}')

        self.assertFalse(self.cli.session_store._record_path(saved_name).is_file())
        self.assertIsNone(self.cli.active_name)
        self.assertIn('Deleted session', mock_output.call_args[0][0])

    @mock.patch.object(tui.printer, 'error')
    def test_delete_unknown_session_lists_available(self, mock_error: mock.MagicMock) -> None:
        self.cli.session_store.save('keeper', _make_agent_session('hello'))

        self.cli.process_user_input('/delete nope')

        self.assertIn('keeper', mock_error.call_args.kwargs['description'])

    @mock.patch.object(tui.printer, 'error')
    def test_process_command_unknown_reports_error(self, mock_error: mock.MagicMock) -> None:
        should_continue = self.cli.process_user_input('/nope')

        self.assertTrue(should_continue)
        mock_error.assert_called_once()


class TestSessionBannerLine(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.store = SessionStore(Path(self.temp_directory_context.name) / 'sessions')

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_banner_line_empty_state(self) -> None:
        line = session_banner_line(self.store)

        self.assertEqual(line, 'none yet - the first turn is saved automatically')

    def test_banner_line_with_sessions(self) -> None:
        self.store.save('2026-10-31-fix-the-login-bug', _make_agent_session('Fix the login bug'))

        line = session_banner_line(self.store)

        self.assertIn('1 saved, latest: 2026-10-31-fix-the-login-bug', line)
        self.assertIn('/resume 2026-10-31-fix-the-login-bug', line)
