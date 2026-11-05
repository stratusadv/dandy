import sys

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.application.agent.intelligence.tools.question.question_tool import QuestionTool
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

        with self.term.cbreak():
            sys.stdout.write(self._input_prefix)
            sys.stdout.flush()

            self._processing_input = True

            while self._processing_input:
                key = self.term.inkey(timeout=None)

                if key.name == 'KEY_ESCAPE' or key == '\x1b':
                    self._escape_count += 1

                    if self._escape_count >= 2:
                        self._escape_exit = True
                        self._processing_input = False

                    continue

                self._escape_count = 0

                if key.name == 'KEY_ENTER' or key in {'\n', '\r'}:
                    self._process_enter_key()

                elif key.name == 'KEY_BACKSPACE' or key in {'\x7f', '\x08'}:
                    self._process_backspace_key()

                elif not key.is_sequence:
                    self._process_key(key)

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

    def _process_enter_key(self) -> None:
        if self._buffer:
            sys.stdout.write('\n')
            sys.stdout.flush()

            self._processing_input = False

    def _process_backspace_key(self) -> None:
        if self._buffer:
            self._buffer.pop()
            # Redraw line
            sys.stdout.write('\r' + self.term.clear_eol())
            sys.stdout.write(self._input_prefix + ''.join(self._buffer))
            sys.stdout.flush()

    def _process_key(self, key: Keystroke) -> None:
        self._buffer.append(key)
        sys.stdout.write(key)
        sys.stdout.flush()


tui = Tui()
