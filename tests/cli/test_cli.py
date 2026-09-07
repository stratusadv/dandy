from unittest import TestCase, mock

from dandy.cli.cli import DandyCli
from dandy.cli.tui.tui import tui


class TestDandyCli(TestCase):
    def setUp(self) -> None:
        with mock.patch.object(tui.printer, 'welcome'):
            self.cli = DandyCli()

    @mock.patch.object(tui, 'get_user_input', return_value=None)
    def test_run_exits_when_escape_pressed_twice(self, mock_get_user_input) -> None:
        self.cli.run()

        mock_get_user_input.assert_called_once_with()

    @mock.patch.object(tui, 'get_user_input', return_value='/quit')
    def test_run_exits_on_quit_command(self, mock_get_user_input) -> None:
        self.cli.run()

        mock_get_user_input.assert_called_once_with()

    @mock.patch('dandy.cli.agent.coding_agent.CodingAgent.chat')
    @mock.patch.object(tui.printer, 'green_divider')
    @mock.patch.object(tui.printer, 'output')
    def test_process_user_input_sends_plain_text_to_agent(
        self, mock_output, mock_green_divider, mock_chat
    ) -> None:
        mock_chat.return_value = mock.MagicMock()
        mock_chat.return_value.text = 'answer'

        should_continue = self.cli.process_user_input('hello there')

        self.assertTrue(should_continue)
        mock_chat.assert_called_once()
        mock_green_divider.assert_called_once_with()
        mock_output.assert_called_once_with('answer')

    @mock.patch('dandy.cli.agent.coding_agent.CodingAgent.chat', side_effect=RuntimeError('boom'))
    @mock.patch.object(tui.printer, 'error')
    def test_process_agent_input_reports_error_on_failure(self, mock_error, mock_chat) -> None:
        should_continue = self.cli.process_user_input('do something')

        self.assertTrue(should_continue)
        mock_error.assert_called_once_with(error='Coding agent failed', description='boom')

    @mock.patch.object(tui.printer, 'output')
    def test_process_command_clear_resets_history(self, mock_output) -> None:
        self.cli.agent.chat = mock.MagicMock()

        should_continue = self.cli.process_user_input('/clear')

        self.assertTrue(should_continue)
        mock_output.assert_called_once()

    @mock.patch.object(tui.printer, 'error')
    def test_process_command_unknown_reports_error(self, mock_error) -> None:
        should_continue = self.cli.process_user_input('/nope')

        self.assertTrue(should_continue)
        mock_error.assert_called_once()
