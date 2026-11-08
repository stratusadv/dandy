import sys

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.application.agent.intelligence.tools.question.question_tool import QuestionTool
from dandy.interfaces.cli.commands import commands_matching_prefix
from dandy.interfaces.cli.tui.printer import Printer
from dandy.interfaces.cli.tui.text import linkify_file_paths

tui_terminal = Terminal()


class Tui:
    def __init__(self) -> None:
        self.term = tui_terminal
        self.printer = Printer(tui_terminal)

        self._buffer = []
        self._input_prefix = self.term.bold_blue('🎩 ')
        self._processing_input = False
        self._escape_count = 0
        self._escape_exit = False
        self._suggestion_visible = False
        self._suggestions_enabled = False

    def clear(self) -> None:
        print(self.term.clear)

    def get_user_input(
        self, question: str | None = None, choices: list[str] | None = None
    ) -> str | None:
        if question:
            self._input_prefix = self.term.purple('⦿ ')
            self.printer.event(
                text=f'\n{self.term.purple}{QuestionTool.action_label}{self.term.normal}'
            )
            self.printer.event(
                text=f'{self.term.purple}↳{self.term.normal} {linkify_file_paths(question)}'
            )

            for index, choice in enumerate(choices or [], start=1):
                self.printer.event(text=f'{self.term.purple}{index}){self.term.normal} {choice}')

            self.printer.purple_divider()

        else:
            self._input_prefix = self.term.bold_blue('⦿ ')
            self.printer.bold_blue_divider()

        self._buffer = []
        self._escape_count = 0
        self._escape_exit = False
        self._suggestion_visible = False
        self._suggestions_enabled = question is None

        with self.term.cbreak():
            sys.stdout.write(self._input_prefix)
            sys.stdout.flush()

            self._processing_input = True

            while self._processing_input:
                self._dispatch_key(self.term.inkey(timeout=None))

        if self._suggestion_visible:
            self._render(clear_suggestion=True)

        if question:
            self.printer.purple_divider()
        else:
            self.printer.blue_divider()

        if self._escape_exit:
            sys.stdout.write('\n')
            sys.stdout.flush()
            return None

        text = ''.join(self._buffer)

        if choices:
            return self._choice_from_text(text, choices)

        return text

    @staticmethod
    def _choice_from_text(text: str, choices: list[str]) -> str:
        stripped = text.strip()

        if stripped.isdigit():
            index = int(stripped)

            if 1 <= index <= len(choices):
                return choices[index - 1]

        return text

    def _dispatch_key(self, key: Keystroke) -> None:
        if key.name == 'KEY_ESCAPE' or key == '\x1b':
            self._escape_count += 1

            if self._escape_count >= 2:
                self._escape_exit = True
                self._processing_input = False

            return

        self._escape_count = 0

        if key.name == 'KEY_ENTER' or key in {'\n', '\r'}:
            self._process_enter_key()

        elif key.name == 'KEY_BACKSPACE' or key in {'\x7f', '\x08'}:
            self._process_backspace_key()

        elif key.name == 'KEY_TAB' or key == '\t':
            self._process_tab_key()

        elif not key.is_sequence:
            self._process_key(key)

    def _process_enter_key(self) -> None:
        if self._buffer:
            self._render(clear_suggestion=True)
            sys.stdout.write('\n')
            sys.stdout.flush()
            self._processing_input = False

    def _process_backspace_key(self) -> None:
        if self._buffer:
            self._buffer.pop()
            self._render()

    def _process_key(self, key: Keystroke) -> None:
        self._buffer.append(key)
        self._render()

    def _process_tab_key(self) -> None:
        if not self._suggestions_enabled:
            return

        matches = self._command_matches()

        if not matches:
            return

        prefix = ''.join(self._buffer)[1:].lower()

        if len(matches) == 1:
            completed = f'/{matches[0]}'
        else:
            common = matches[0]

            for match in matches[1:]:
                while not match.startswith(common):
                    common = common[:-1]

            if common == prefix:
                return

            completed = f'/{common}'

        self._buffer = list(completed)
        self._render()

    def _render(self, clear_suggestion: bool = False) -> None:
        text = '' if clear_suggestion else self._suggestion_text()
        suggestion = self.term.grey(text) if text else ''
        prefix_and_buffer = self._input_prefix + ''.join(self._buffer)
        sys.stdout.write('\r' + self.term.clear_eol() + prefix_and_buffer + suggestion)
        self._suggestion_visible = bool(text)
        sys.stdout.flush()

    def _command_matches(self) -> list[str]:
        text = ''.join(self._buffer)

        if not text.startswith('/') or ' ' in text or '\t' in text:
            return []

        prefix = text[1:].lower()
        return [command.name for command in commands_matching_prefix(prefix)]

    def _suggestion_text(self) -> str:
        if not self._suggestions_enabled:
            return ''

        matches = self._command_matches()

        if not matches:
            return ''

        text = '  ' + '   '.join(f'/{match}' for match in matches)
        line_length = self.term.length(self._input_prefix) + self.term.length(
            ''.join(self._buffer) + text
        )

        if line_length > self.term.width:
            return ''

        return text


tui = Tui()
