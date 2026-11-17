import sys

from dandy.application.agent.attachments import detect_attachment_paths, prepare_turn_attachments
from dandy.application.agent.cli.intelligence.bots.session_naming_bot import SessionNamingBot
from dandy.application.agent.cli.cli_agent import CliAgent
from dandy.application.agent.exceptions import AgentExternalError
from dandy.application.agent.intel import SessionRecord
from dandy.application.agent.session import session
from dandy.application.agent.session_store import SessionStore
from dandy.application.skill.loader import load_cli_skills
from dandy.interfaces.cli.commands import command_choices, resolve
from dandy.interfaces.cli.error_log import log_cli_error
from dandy.interfaces.cli.tui.tui import tui
from dandy.shared.cancellation import stop_signal
from dandy.shared.constants import AGENTS_MD_FILE_NAME
from dandy.shared.exceptions import RunStoppedError
from dandy.shared.interaction import question_gate
from dandy.shared.settings import settings

# Tool name to (path argument, action) for the tools whose calls show up in the
# file sections the CLI prints below the final answer.
FILE_TOOL_ACTIONS = {
    'write_file': ('file_path', 'added'),
    'edit_file': ('file_path', 'modified'),
    'delete_file': ('file_path', 'removed'),
    'create_directory': ('directory_path', 'added'),
}


def session_name_for_request(naming_bot: SessionNamingBot, request_text: str) -> str:
    try:
        naming_bot.reset()
        intel = naming_bot.process(request_text)
    except Exception as error:
        log_cli_error(session.project_base_path, 'session naming', error)
        return request_text

    name = intel.name.strip()

    return name or request_text


class DandyCli:
    def __init__(self) -> None:
        skills, skill_issues = load_cli_skills(session.project_base_path)
        self.agent = CliAgent(ask_user=self._ask_user, skills=skills)
        self.session_naming_bot = SessionNamingBot()
        self.verbose_callback = DandyCli._emit_verbose if DandyCli._is_debug_enabled() else None
        self.session_store = SessionStore.for_project(session.project_base_path)
        self.active_name: str | None = None
        self.last_turn_succeeded: bool = True

        for issue in skill_issues:
            tui.printer.error(error='Skill skipped', description=issue)

    @staticmethod
    def _is_debug_enabled() -> bool:
        """Whether settings DEBUG enables verbose tracing of the agent loop."""
        return bool(getattr(settings, 'DEBUG', False))

    @staticmethod
    def _emit_verbose(message: str) -> None:
        sys.stdout.write(f'\r   ↳ {message}\n')
        sys.stdout.flush()

    @staticmethod
    def _ask_user(question: str, choices: list[str]) -> str:
        """Block the agent until the user answers its question (stop-safe)."""
        return question_gate.ask(question, choices, stop_signal)

    @staticmethod
    def _prompt_question(question: str, choices: list[str]) -> str | None:
        """The UI side of an agent question: one prompt on the main thread."""
        return tui.get_user_input(question=question, choices=choices)

    def process_user_input(self, user_input: str) -> bool:
        """Process one user input, returning False to stop the loop.

        The outcome of an agent turn is recorded on ``last_turn_succeeded``;
        one-shot mode uses it to set the process exit code without changing
        the REPL behavior of continuing after a failed turn.
        """
        if user_input.startswith('/'):
            return self.process_command(user_input)

        self.last_turn_succeeded = self.process_agent_input(user_input)
        return True

    def process_command(self, user_input: str) -> bool:
        parts = user_input.split(' ', 1)
        command_word = parts[0][1:].lower()
        argument = parts[1].strip() if len(parts) > 1 else ''

        command = resolve(command_word)

        if command is None:
            if command_word == 'exit':
                return False

            tui.printer.error(
                error='Unknown command',
                description=f'"{command_word}" is not a valid command. Try {command_choices()}.',
            )
            return True

        if command.name == 'quit':
            return False

        if command.name == 'paste':
            return self._process_paste()

        handlers = {
            'init': (self._process_init, ()),
            'new': (self._process_new, (argument,)),
            'sessions': (self._process_sessions, (argument,)),
            'resume': (self._process_resume, (argument,)),
            'delete': (self._process_delete, (argument,)),
        }

        handler, handler_arguments = handlers[command.name]
        return handler(*handler_arguments)

    def _process_paste(self) -> bool:
        tui.printer.output('Paste multi-line text, then press Ctrl-D to send it.')

        try:
            text = ''.join(list(sys.stdin)).strip()
        except KeyboardInterrupt:
            tui.printer.output('Paste cancelled.')
            return True

        if not text:
            tui.printer.output('Nothing was pasted; the input was discarded.')
            return True

        self.last_turn_succeeded = self.process_agent_input(text)
        return True

    def _process_init(self) -> bool:
        self.run_init()

        return True

    def _process_new(self, name: str) -> bool:
        self.agent.clear()
        self.active_name = name or None

        if name:
            tui.printer.output(f'Started a new conversation to be saved as "{name}".')
        else:
            tui.printer.output('Started a new conversation.')

        return True

    def _process_sessions(self, name: str) -> bool:
        if name:
            return self._process_resume(name)

        self.print_sessions()

        return True

    def _session_row(self, number: int, record: SessionRecord) -> str:
        name = f'**{record.name}**' if record.name == self.active_name else record.name

        return f'| {number} | {name} |'

    def resolve_session_selection(self, selection: str) -> str | None:
        """Resolve a typed row number or session name, printing the error and None on a miss."""
        try:
            return self.session_store.resolve_selection(selection)
        except AgentExternalError as error:
            tui.printer.error(error='Could not resume session', description=str(error))
            return None

    def _process_resume(self, selection: str) -> bool:
        if not selection:
            self.load_latest_session()
            return True

        name = self.resolve_session_selection(selection)

        if name is None:
            return True

        self.load_named_session(name)

        return True

    def load_named_session(self, name: str) -> bool:
        """Load a saved session into the agent, returning whether it succeeded.

        Shared by the /resume (and /s <name>) command and by one-shot mode,
        which uses the return value as the process exit code.
        """
        try:
            agent_session = self.session_store.load(name)
        except AgentExternalError as error:
            tui.printer.error(error='Could not resume session', description=str(error))
            return False

        self.agent.load_session(agent_session)
        self.active_name = name
        tui.printer.output(f'Resumed session "{name}".')

        return True

    def load_latest_session(self) -> bool:
        """Load the project's most recently saved session into the agent, if any."""
        latest_name = self.session_store.latest()

        if latest_name is None:
            tui.printer.error(
                error='No session to resume',
                description='There are no saved sessions for this project yet.',
            )
            return False

        return self.load_named_session(latest_name)

    def _process_delete(self, name: str) -> bool:
        if not name:
            tui.printer.error(error='Usage', description='/delete <name>')
            return True

        self.run_delete(name)

        return True

    def run_sessions_list(self) -> bool:
        """Print the saved-sessions table; the one-shot listing always succeeds."""
        self.print_sessions()

        return True

    def print_sessions(self) -> None:
        records = self.session_store.list_sessions()

        if not records:
            tui.printer.output('No sessions saved yet. The first turn saves this conversation.')
            return

        oldest_first = sorted(records, key=lambda record: record.updated_at)
        table = (
            '| # | Session |\n'
            '|---|---|\n'
            + '\n'.join(
                self._session_row(number, record)
                for number, record in enumerate(oldest_first, start=1)
            )
            + '\n\nResume one with `/r <row>` or its name — the newest is on the bottom row.'
        )

        tui.printer.output(table)

    def run_in_session(self, selection: str | None, request: str) -> bool:
        """Resume a saved session (the latest if no name) and run one turn inside it.

        `selection` is a row number from the /s table or a session name.
        """
        if selection is None:
            if not self.load_latest_session():
                return False
        else:
            name = self.resolve_session_selection(selection)

            if name is None:
                return False

            if not self.load_named_session(name):
                return False

        self.process_user_input(request)

        return self.last_turn_succeeded

    def run_new_one_shot(self, name: str | None, request: str) -> bool:
        """Start a fresh (optionally pre-named) conversation and run one turn."""
        self._process_new(name or '')
        self.process_user_input(request)

        return self.last_turn_succeeded

    def run_delete(self, name: str) -> bool:
        """Delete a saved session, returning whether it succeeded (one-shot mode)."""
        try:
            self.session_store.delete(name)
        except AgentExternalError as error:
            tui.printer.error(error='Could not delete session', description=str(error))
            return False

        if self.active_name == name:
            self.active_name = None

        tui.printer.output(f'Deleted session "{name}".')

        return True

    def process_agent_input(self, user_input: str) -> bool:
        stop_signal.clear()

        succeeded = True
        file_actions: dict[str, str] = {}

        def record_tool_call(name: str, arguments: dict[str, object]) -> None:
            entry = FILE_TOOL_ACTIONS.get(name)

            if entry is None:
                return

            param, action = entry
            path = arguments.get(param)

            if isinstance(path, str) and path:
                file_actions[path] = action

        text, attachment_paths = detect_attachment_paths(user_input, session.project_base_path)
        attachments, attachment_issues = prepare_turn_attachments(
            attachment_paths, session.project_base_path
        )

        for attachment in attachments:
            if attachment.kind == 'project_file':
                tui.printer.output(
                    f'Saved "{attachment.source_path.name}" to {attachment.delivery_path}'
                )
            else:
                tui.printer.output(f'Attached "{attachment.source_path.name}" ({attachment.kind})')

        for issue in attachment_issues:
            tui.printer.error(error='Attachment failed', description=issue)

        try:
            result_intel = tui.printer.run_timed_task(
                task=text[:80],
                work=lambda update: self.agent.turn(
                    text,
                    progress_callback=update,
                    verbose_callback=self.verbose_callback,
                    tool_call_callback=record_tool_call,
                    attachments=attachments,
                ),
                stop_signal=stop_signal,
                question_gate=question_gate,
                question_handler=self._prompt_question,
            )
        except RunStoppedError:
            tui.printer.output('Run stopped.')
        except Exception as error:
            log_cli_error(session.project_base_path, 'agent turn', error)
            tui.printer.error(error='Dandy ran into an error', description=str(error))
            succeeded = False
        else:
            added_files = [path for path, action in file_actions.items() if action == 'added']
            modified_files = [path for path, action in file_actions.items() if action == 'modified']
            removed_files = [path for path, action in file_actions.items() if action == 'removed']

            tui.printer.bold_green_divider()
            tui.printer.output(result_intel.text)
            tui.printer.file_change_sections(added_files, modified_files, removed_files)
        finally:
            self._save_session_after_turn(user_input)

        return succeeded

    def run_init(self) -> bool:
        """Run the AGENTS.md generation pass, returning whether it succeeded.

        Used by the /init command and by one-shot mode; the outcome doubles as
        the one-shot process exit code.
        """
        stop_signal.clear()

        try:
            summary = tui.printer.run_timed_task(
                task=f'{AGENTS_MD_FILE_NAME} for {session.project_base_path}',
                work=lambda update: self.agent.run_init_pass(
                    progress_callback=update, verbose_callback=self.verbose_callback
                ),
                stop_signal=stop_signal,
            )
        except RunStoppedError:
            tui.printer.output('Run stopped.')
            return False
        except Exception as error:
            log_cli_error(session.project_base_path, 'init', error)
            tui.printer.error(error='Init failed', description=str(error))
            return False

        if summary is None:
            tui.printer.error(
                error='Init failed', description=f'The agent did not write {AGENTS_MD_FILE_NAME}.'
            )
            return False

        tui.printer.bold_green_divider()
        tui.printer.output(summary)
        tui.printer.output(
            f'Wrote {AGENTS_MD_FILE_NAME} ({session.agents_md_path.stat().st_size} bytes); '
            'it is now part of the agent system prompt.'
        )

        return True

    def _save_session_after_turn(self, user_input: str) -> None:
        if len(self.agent.history) == 0:
            return

        if self.active_name is None:
            self.active_name = self.session_store.new_name(
                session_name_for_request(self.session_naming_bot, user_input)
            )

        self.session_store.save(self.active_name, self.agent.save_session())

    def run(self, new_name: str | None = None) -> None:
        if new_name is not None:
            self.agent.clear()
            self.active_name = new_name or None

        tui.printer.welcome()

        try:
            while True:
                user_input = tui.get_user_input()

                if user_input is None:
                    break

                if not self.process_user_input(user_input):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            stop_signal.set()

        tui.printer.bold_green_divider()
        tui.printer.output('Bye')
