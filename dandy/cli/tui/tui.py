import sys

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.cli.tui.printer import Printer

tui_terminal = Terminal()


class Tui:
    def __init__(self):
        self.term = tui_terminal
        self.printer = Printer(tui_terminal)

        self._buffer = []
        self._input_prefix = self.term.bold_blue('🎩 ')
        self._processing_input = False
        self._escape_count = 0
        self._escape_exit = False

    def clear(self):
        print(self.term.clear)

    def get_user_input(self, question: str | None = None) -> str | None:
        if question:
            self._input_prefix = self.term.purple('⦿ ')
            self.printer.indented_event(
                text=f'{self.term.purple}Question: {self.term.normal}{question}', indent=1
            )
            self.printer.purple_divider()

        else:
            self._input_prefix = self.term.bold_blue('⦿ ')
            self.printer.blue_divider()

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
            self.printer.divider()

        if self._escape_exit:
            sys.stdout.write('\n')
            sys.stdout.flush()
            return None

        return ''.join(self._buffer)

    def _process_enter_key(self):
        if self._buffer:
            sys.stdout.write('\n')
            sys.stdout.flush()

            self._processing_input = False

    def _process_backspace_key(self):
        if self._buffer:
            self._buffer.pop()
            # Redraw line
            sys.stdout.write('\r' + self.term.clear_eol())
            sys.stdout.write(self._input_prefix + ''.join(self._buffer))
            sys.stdout.flush()

    def _process_key(self, key: Keystroke):
        self._buffer.append(key)
        sys.stdout.write(key)
        sys.stdout.flush()


tui = Tui()
