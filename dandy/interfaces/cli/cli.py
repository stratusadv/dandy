import sys

from dandy.application.agent.coding_agent import CodingAgent
from dandy.application.agent.exceptions import AgentRecoverableError
from dandy.application.agent.intel import SessionRecord
from dandy.application.agent.session import session
from dandy.application.agent.session_store import SessionStore
from dandy.interfaces.cli.tui.tui import tui
from dandy.shared.settings import settings

CLI_COMMANDS = ('new', 'sessions', 'resume', 'delete', 'quit')


class DandyCli:
    def __init__(self) -> None:
        self.agent = CodingAgent()
        self.verbose_callback = DandyCli._emit_verbose if DandyCli._is_debug_enabled() else None
        self.session_store = SessionStore.for_project(session.project_base_path)
        self.active_name: str | None = None

    @staticmethod
    def _is_debug_enabled() -> bool:
        """Whether settings DEBUG enables verbose tracing of the agent loop."""
        return bool(getattr(settings, 'DEBUG', False))

    @staticmethod
    def _emit_verbose(message: str) -> None:
        sys.stdout.write(f'\r   ↳ {message}\n')
        sys.stdout.flush()

    def process_user_input(self, user_input: str, save_session: bool = True) -> bool:
        """Process one user input, returning False to stop the loop."""
        if user_input.startswith('/'):
            return self.process_command(user_input)

        self.process_agent_input(user_input, save_session=save_session)
        return True

    def process_command(self, user_input: str) -> bool:
        parts = user_input.split(' ', 1)
        command = parts[0][1:].lower()
        argument = parts[1].strip() if len(parts) > 1 else ''

        if command == 'new':
            return self._process_new(argument)

        if command == 'sessions':
            return self._process_sessions()

        if command == 'resume':
            return self._process_resume(argument)

        if command == 'delete':
            return self._process_delete(argument)

        if command in {'exit', 'quit', 'q'}:
            return False

        tui.printer.error(
            error='Unknown command',
            description=f'"{command}" is not a valid command. Try {tuple(CLI_COMMANDS)}.',
        )
        return True

    def _process_new(self, name: str) -> bool:
        self.agent.clear()
        self.active_name = name or None

        if name:
            tui.printer.output(f'Started a new conversation to be saved as "{name}".')
        else:
            tui.printer.output('Started a new conversation.')

        return True

    def _process_sessions(self) -> bool:
        records = self.session_store.list_sessions()

        if not records:
            tui.printer.output('No sessions saved yet. The first turn saves this conversation.')
            return True

        table = (
            '| Session | Updated | Messages | Tokens | Model |\n'
            '|---|---|---|---|---|\n' + '\n'.join(self._session_row(record) for record in records)
        )

        tui.printer.output(table)

        return True

    def _session_row(self, record: SessionRecord) -> str:
        name = f'**{record.name}**' if record.name == self.active_name else record.name
        updated_at = record.updated_at.strftime('%Y-%m-%d %H:%M')
        message_count = len(record.session.messages)
        token_count = record.session.token_count
        model_name = record.session.model or '-'

        return f'| {name} | {updated_at} | {message_count} | {token_count} | {model_name} |'

    def _process_resume(self, name: str) -> bool:
        if not name:
            tui.printer.error(error='Usage', description='/resume <name>')
            return True

        try:
            agent_session = self.session_store.load(name)
        except AgentRecoverableError as error:
            tui.printer.error(error='Could not resume session', description=str(error))
            return True

        self.agent.load_session(agent_session)
        self.active_name = name
        tui.printer.output(f'Resumed session "{name}".')

        return True

    def _process_delete(self, name: str) -> bool:
        if not name:
            tui.printer.error(error='Usage', description='/delete <name>')
            return True

        try:
            self.session_store.delete(name)
        except AgentRecoverableError as error:
            tui.printer.error(error='Could not delete session', description=str(error))
            return True

        if self.active_name == name:
            self.active_name = None

        tui.printer.output(f'Deleted session "{name}".')

        return True

    def process_agent_input(self, user_input: str, save_session: bool = True) -> bool:
        tui.printer.running_phrase('Coding')

        try:
            result_intel = tui.printer.run_timed_task(
                action_name='Coding',
                task=user_input[:80],
                work=lambda update: self.agent.turn(
                    user_input, progress_callback=update, verbose_callback=self.verbose_callback
                ),
            )
        except Exception as error:
            tui.printer.error(error='Coding agent failed', description=str(error))
            return False

        tui.printer.green_divider()
        tui.printer.output(result_intel.text)

        if save_session:
            self._save_session_after_turn(user_input)

        return True

    def continue_latest_session(self, user_input: str) -> None:
        """Run one turn inside the project's most recently saved session."""
        latest_name = self.session_store.latest()

        if latest_name is None:
            tui.printer.error(
                error='No session to continue',
                description='There are no saved sessions for this project yet.',
            )
            return

        self.agent.load_session(self.session_store.load(latest_name))
        self.active_name = latest_name
        tui.printer.output(f'Continuing session "{latest_name}".')

        turn_succeeded = self.process_agent_input(user_input, save_session=False)

        if turn_succeeded and len(self.agent.history) > 0:
            self.session_store.save(self.active_name, self.agent.save_session())
            tui.printer.output(
                f'Saved session "{self.active_name}" ({len(self.agent.history)} messages).'
            )

    def _save_session_after_turn(self, user_input: str) -> None:
        if len(self.agent.history) == 0:
            return

        if self.active_name is None:
            self.active_name = self.session_store.new_name(user_input)

        self.session_store.save(self.active_name, self.agent.save_session())

    def run(self) -> None:
        tui.printer.welcome()

        while True:
            user_input = tui.get_user_input()

            if user_input is None:
                break

            if not self.process_user_input(user_input):
                break

        tui.printer.green_divider()
