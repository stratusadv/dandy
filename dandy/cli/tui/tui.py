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
        self._action_commands = []
        self._last_autocomplete_text = ''
        self._match_index = 0
        self._current_matches = []
        self._hint_lines = 0
        self._input_prefix = self.term.bold_blue('🎩 ')
        self._processing_input = False

    def clear(self):
        print(self.term.clear)

    def _get_matching_actions(self, text: str) -> list[str]:
        if not text.startswith('/'):
            return []

        text_without_slash = text[1:]
        matches = [
            f'/{cmd}'
            for cmd in self._action_commands
            if cmd.startswith(text_without_slash)
        ]
        return matches

    def setup_autocomplete(self, action_commands: list):
        self._action_commands = action_commands

    def _display_autocomplete_hints(self, action_matches: list, selected_index: int) -> int:
        if not action_matches:
            return 0

        # Clear previous hints - use gray color instead of dim for Windows compatibility
        hint_text = self.term.bold_blue('  Options: ')
        for i, match in enumerate(action_matches):
            if i == selected_index:
                hint_text += self.term.bold_cyan(f'{match} ')
            else:
                hint_text += self.term.gray(f'{match} ')

        sys.stdout.write('\n' + hint_text)
        sys.stdout.flush()

        return 1  # Number of lines used for hints

    def _clear_hint_lines(self):
        if self._hint_lines > 0:
            for _ in range(self._hint_lines):
                sys.stdout.write(self.term.move_down(1))
            sys.stdout.write('\r' + self.term.clear_eol())
            for _ in range(self._hint_lines):
                sys.stdout.write(self.term.move_up(1))

    def get_user_input(self, question: str | None = None) -> str:
        if question:
            self._input_prefix = self.term.purple('⦿ ')
            self.printer.indented_event(
                text=f'{self.term.purple}Question: {self.term.normal}{question}',
                indent=1
            )
            self.printer.purple_divider()

        else:
            self._input_prefix = self.term.bold_blue('⦿ ')
            self.printer.blue_divider()

        self._buffer = []
        self._match_index = 0
        self._current_matches = []
        self._hint_lines = 0

        with self.term.cbreak():
            sys.stdout.write(self._input_prefix)
            sys.stdout.flush()

            self._processing_input = True

            while self._processing_input:
                key = self.term.inkey(timeout=None)

                if key.name == 'KEY_ENTER' or key in {'\n', '\r'}:
                    self._process_enter_key()

                elif key.name == 'KEY_BACKSPACE' or key in {'\x7f', '\x08'}:
                    self._process_backspace_key()

                elif key.name == 'KEY_TAB' or key == '\t':
                    self._process_tab_key()

                elif not key.is_sequence:
                    self._process_key(key)

        if question:
            self.printer.divider()

        return ''.join(self._buffer)

    def _process_enter_key(self):
        if self._buffer:
            self._clear_hint_lines()
            sys.stdout.write('\n')
            sys.stdout.flush()

            self._processing_input = False

    def _process_backspace_key(self):
        if self._buffer:
            self._buffer.pop()
            self._clear_hint_lines()
            self._hint_lines = 0
            # Redraw line
            sys.stdout.write('\r' + self.term.clear_eol())
            sys.stdout.write(self._input_prefix + ''.join(self._buffer))

            # Check for new matches after backspace
            current_text = ''.join(self._buffer)
            if current_text.startswith('/') and len(current_text) > 1:
                self._current_matches = self._get_matching_actions(current_text)
                self._match_index = 0
                # Display hints
                if self._current_matches:
                    self._show_hints()
            else:
                self._current_matches = []
                self._match_index = 0

            sys.stdout.flush()

    def _process_tab_key(self):
        # Tab pressed - autocomplete
        current_text = ''.join(self._buffer)
        if not self._current_matches or current_text != self._last_autocomplete_text:
            self._current_matches = self._get_matching_actions(current_text)
            self._match_index = 0
            self._last_autocomplete_text = current_text

        if self._current_matches:
            # Cycle through matches
            self._buffer = list(
                self._current_matches[self._match_index % len(self._current_matches)]
            )

            self._clear_hint_lines()

            # Redraw line
            sys.stdout.write('\r' + self.term.clear_eol())
            sys.stdout.write(self._input_prefix + ''.join(self._buffer))

            # Display hints
            self._hint_lines = self._display_autocomplete_hints(
                self._current_matches, self._match_index % len(self._current_matches)
            )

            # Move cursor back to input line
            for _ in range(self._hint_lines):
                sys.stdout.write(self.term.move_up(1))
            sys.stdout.write('\r' + self._input_prefix + ''.join(self._buffer))
            sys.stdout.flush()

            self._match_index += 1

    def _process_key(self, key: Keystroke):
        self._buffer.append(key)
        current_text = ''.join(self._buffer)

        self._clear_hint_lines()

        # Check for new matches
        if current_text.startswith('/') and len(current_text) > 1:
            self._current_matches = self._get_matching_actions(current_text)
            self._match_index = 0

            # Display new hints
            sys.stdout.write(key)
            self._show_hints()
        else:
            self._current_matches = []
            self._match_index = 0
            self._hint_lines = 0
            sys.stdout.write(key)

        sys.stdout.flush()

    def _show_hints(self):
        self._hint_lines = self._display_autocomplete_hints(
            self._current_matches, -1
        )
        # Move cursor back to input line
        for _ in range(self._hint_lines):
            sys.stdout.write(self.term.move_up(1))

        sys.stdout.write('\r' + self._input_prefix + ''.join(self._buffer))


tui = Tui()
