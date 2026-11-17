import sys

from blessed import Terminal
from blessed.keyboard import Keystroke

from dandy.application.agent.intelligence.tools.question.question_tool import QuestionTool
from dandy.interfaces.cli.commands import commands_matching_prefix
from dandy.interfaces.cli.tui.notify import desktop_notify
from dandy.interfaces.cli.tui.printer import Printer
from dandy.interfaces.cli.tui.text import linkify_file_paths

tui_terminal = Terminal()

_PASTE_START_MARKER = '\x1b[200~'
_PASTE_END_MARKER = '\x1b[201~'

# How long a held marker tail waits for the rest of the marker before it is
# flushed back as ordinary keys. Real paste markers complete within the same
# burst, so anything slower was typed by hand.
_MARKER_HOLD_TIMEOUT = 0.05


def _human_size(byte_count: int) -> str:
    if byte_count < 1024:
        return f'{byte_count} B'
    if byte_count < 1024 * 1024:
        return f'{byte_count / 1024:.1f} KB'
    return f'{byte_count / (1024 * 1024):.1f} MB'


def paste_block_indicator(pasted_text: str) -> str:
    line_count = pasted_text.count('\n') + 1
    return f'⤶ {line_count} lines · {_human_size(len(pasted_text))} pasted'


class Tui:
    def __init__(self) -> None:
        self.term = tui_terminal
        self.printer = Printer(tui_terminal)

        # The input line is a list of blocks: plain characters (typed) and
        # pasted chunks (bracketed pastes), which render as a compact
        # indicator but submit verbatim.
        self._buffer: list[str] = []
        self._paste_blocks: set[int] = set()
        self._input_prefix = self.term.bold_blue('🎩 ')
        self._processing_input = False
        self._escape_count = 0
        self._escape_exit = False
        self._suggestion_visible = False
        self._suggestions_enabled = False
        self._rendered_lines = 1
        self._inside_bracketed_paste = False
        # True once bracketed paste is enabled for this input: blessed's
        # DEC-mode cache marks 2004 SET, so blessed parses a whole paste as a
        # single BRACKETED_PASTE key. When the terminal ignored the enable
        # anyway, the character-level marker fallback below still covers the
        # paste bytes arriving as ordinary keys.
        self._bracketed_paste_native = False
        self._bracketed_paste_we_enabled = False
        # The bytes of a paste marker still being assembled. The terminal may
        # split ESC[200~ / ESC[201~ across several inkey() calls, so the tail
        # is held here until it completes, or a timeout flushes it as
        # ordinary keys when the user just typed an escape by hand.
        self._pending_marker = ''

    def clear(self) -> None:
        print(self.term.clear)

    def get_user_input(
        self, question: str | None = None, choices: list[str] | None = None
    ) -> str | None:
        if question:
            desktop_notify(question, self.term)

            # NB: the heavy-right-quot glyph is the intended question prompt mark.
            self._input_prefix = self.term.purple('❯ ')
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
            self._input_prefix = self.term.bold_blue('❯ ')
            self.printer.bold_blue_divider()

        self._buffer = []
        self._paste_blocks = set()
        self._escape_count = 0
        self._escape_exit = False
        self._suggestion_visible = False
        self._suggestions_enabled = question is None
        self._inside_bracketed_paste = False
        self._bracketed_paste_native = False
        self._pending_marker = ''

        with self.term.cbreak(), self.term.bracketed_paste(timeout=0.25):
            # blessed's bracketed_paste() only sends the DECSET enable when the
            # terminal *answers* the DECRQM probe; a terminal that does not
            # answer (many do) is left with the mode OFF, so it pastes raw
            # newlines and every line submits. Mark the mode SET in blessed's
            # DEC-mode cache and emit the enable ourselves: then blessed
            # parses a whole paste as one BRACKETED_PASTE key no matter what,
            # and the character-level marker fallback below still covers the
            # case where the terminal ignored the enable.
            self._bracketed_paste_native = self._arm_bracketed_paste()

            self._processing_input = True

            sys.stdout.write(self._input_prefix)
            sys.stdout.flush()
            self._rendered_lines = 1

            try:
                self._read_until_submitted()
            finally:
                self._restore_bracketed_paste()

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

    def _read_until_submitted(self) -> None:
        """Loop over keys until the input is submitted or escape-exited."""
        while self._processing_input:
            # While a marker tail is pending, wait with a short timeout: a
            # real marker completes in the same burst, so a timeout means the
            # user typed the escape by hand and the held bytes must come back
            # as ordinary keys.
            timeout = _MARKER_HOLD_TIMEOUT if self._pending_marker else None
            key = self.term.inkey(timeout=timeout)
            self._dispatch_key(key)
            if not self._processing_input:
                break
            if not key:
                self._flush_pending_marker()

    def _restore_bracketed_paste(self) -> None:
        """Turn off bracketed paste if we turned it on for this input.

        blessed's own ``bracketed_paste()`` context manager only resets the
        modes *it* enabled on entry, so the silent-probe case (where it never
        enabled the mode and we armed it ourselves) would otherwise stay on in
        the terminal after the input. We only reset a mode we set, so a
        terminal that had bracketed paste on before is left untouched.
        """
        if not (self._bracketed_paste_we_enabled and self.term.is_a_tty):
            return

        from blessed.dec_modes import DecModeResponse  # noqa: PLC0415

        if self.term._dec_mode_cache.get(2004) == DecModeResponse.SET:
            self.term._dec_mode_cache[2004] = DecModeResponse.RESET
            sys.stdout.write('\x1b[?2004l')
            sys.stdout.flush()

    @staticmethod
    def _choice_from_text(text: str, choices: list[str]) -> str:
        stripped = text.strip()

        if stripped.isdigit():
            index = int(stripped)

            if 1 <= index <= len(choices):
                return choices[index - 1]

        return text

    def _dispatch_key(self, key: Keystroke | str) -> None:
        if not key:
            return

        text = str(key)
        name = getattr(key, 'name', None)

        if name == 'BRACKETED_PASTE':
            # blessed parsed a complete bracketed paste as one keystroke; the
            # .text property is the pasted content.
            self._add_paste_block(getattr(key, 'text', None) or '')

            return

        if name == 'KEY_ESCAPE' or text == '\x1b':
            self._on_escape_key()

            return

        if self._pending_marker:
            # A held escape or CSI may still be the start of a
            # bracketed-paste marker (the terminal did not confirm bracketed
            # paste mode, so blessed fragments the marker: a bare ESC or a
            # lone CSI, then the '200~'/'201~' tail). Keep collecting until
            # the marker completes or a timeout flushes it as ordinary keys.
            self._on_pending_marker_char(text)

            return

        if name == 'CSI' and text == '\x1b[':
            # A bare CSI (ESC + '[') is what blessed resolves a paste marker
            # to when the terminal did not confirm bracketed-paste mode: the
            # ESC is already inside the sequence, and the '200~' / '201~'
            # tail may follow as ordinary keys.
            self._escape_count = 0
            self._pending_marker = text

            return

        if self._inside_bracketed_paste:
            self._on_paste_char(text)

            return

        self._escape_count = 0

        if name == 'KEY_ENTER' or text in {'\n', '\r'}:
            self._process_enter_key()

        elif name == 'KEY_BACKSPACE' or text in {'\x7f', '\x08'}:
            self._process_backspace_key()

        elif name == 'KEY_TAB' or text == '\t':
            self._process_tab_key()

        elif not getattr(key, 'is_sequence', False):
            self._process_key(text)

    def _on_escape_key(self) -> None:
        # The escape may open a bracketed-paste marker (the terminal sends
        # ESC[200~ / ESC[201~). Hold it: if the marker tail completes it is a
        # paste boundary, and if it does not (the user just pressed escape)
        # the double-escape count above still applies. A bare ESC never
        # completes either marker, so holding it can never swallow a
        # double-escape exit.
        self._escape_count += 1
        self._pending_marker = '\x1b'

        if self._escape_count >= 2:
            self._escape_exit = True
            self._processing_input = False

    def _on_pending_marker_char(self, text: str) -> None:
        self._pending_marker += text

        if self._pending_marker == _PASTE_START_MARKER:
            self._pending_marker = ''
            self._escape_count = 0
            self._inside_bracketed_paste = True

            return

        if self._pending_marker == _PASTE_END_MARKER:
            # The paste content already landed in its own block via
            # _on_paste_char; closing the paste just flips the flag so the
            # next typed character starts a fresh block again.
            self._pending_marker = ''
            self._escape_count = 0
            self._inside_bracketed_paste = False

            return

        if not any(
            marker.startswith(self._pending_marker)
            for marker in (_PASTE_START_MARKER, _PASTE_END_MARKER)
        ):
            self._flush_pending_marker()

    def _arm_bracketed_paste(self) -> bool:
        """Enable bracketed paste even when the terminal's probe went silent.

        ``term.bracketed_paste()`` (a blessed context manager) emits the DECSET
        enable only when the terminal answered its DECRQM probe. A terminal
        that did not answer (Konsole among them) is left with the mode OFF, so
        it would paste raw newlines and the input line would submit every
        line. Here we emit the enable ourselves when the mode is not already
        enabled and record it as SET in blessed's DEC-mode cache, which also
        makes blessed parse a complete paste as a single BRACKETED_PASTE
        keystroke. Returns True when blessed now parses pastes natively; the
        character-level marker handling in the dispatch loop still covers the
        case where the terminal ignored the enable (its marker bytes then
        stream in as ordinary keys).
        """
        from blessed.dec_modes import DecModeResponse  # noqa: PLC0415

        if not self.term.does_styling:
            return False

        if self.term._dec_mode_cache.get(2004) != DecModeResponse.SET:
            self.term._dec_mode_cache[2004] = DecModeResponse.SET
            self._bracketed_paste_we_enabled = True

            if self.term.is_a_tty:
                sys.stdout.write('\x1b[?2004h')
                sys.stdout.flush()

        return True

    def _flush_pending_marker(self) -> None:
        # The marker never completed: the escape (and any stray bytes that
        # followed it) were typed by hand. The ESC itself is swallowed, like a
        # stray escape, but its double-escape count is kept so a slow
        # double-escape still exits; any other bytes are replayed through the
        # dispatcher (so a stray newline or backspace still acts on the
        # input). A replayed key resets the count itself, as it normally would.
        marker = self._pending_marker
        self._pending_marker = ''

        for character in marker:
            if character == '\x1b':
                continue
            self._dispatch_key(character)

    def _add_paste_block(self, text: str) -> None:
        self._buffer.append(text)
        self._paste_blocks.add(len(self._buffer) - 1)
        self._render()

    def _on_paste_char(self, text: str) -> None:
        if self._inside_bracketed_paste:
            # Paste content always lands in the current paste block (or a new
            # one if the last block is a typed character), so a whole paste
            # stays one block that a backspace removes at once.
            if not self._buffer or len(self._buffer) - 1 not in self._paste_blocks:
                self._buffer.append('')
                self._paste_blocks.add(len(self._buffer) - 1)

            index = len(self._buffer) - 1
            self._buffer[index] += text
            self._render()

            return

        # Outside a paste this only happens for characters replayed by a
        # marker flush; they are plain typed input again.
        self._process_key(text)

    def _process_enter_key(self) -> None:
        if self._buffer:
            self._render(clear_suggestion=True)
            sys.stdout.write('\n')
            sys.stdout.flush()
            self._processing_input = False

    def _process_backspace_key(self) -> None:
        if not self._buffer:
            return

        # A paste block is one unit (it renders as one indicator), so a
        # backspace removes the whole block at once.
        self._buffer.pop()
        self._paste_blocks.discard(len(self._buffer))
        self._render()

    def _process_key(self, key: Keystroke | str) -> None:
        self._buffer.append(str(key))
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
        self._paste_blocks = set()
        self._render()

    def _render(self, clear_suggestion: bool = False) -> None:
        text = '' if clear_suggestion else self._suggestion_text()
        suggestion = self.term.grey(text) if text else ''
        line = self._input_prefix + self._display_text() + suggestion
        sys.stdout.write(self._clear_rendered_lines() + line)
        self._rendered_lines = self._visual_line_count(line)
        self._suggestion_visible = bool(text)
        sys.stdout.flush()

    def _display_text(self) -> str:
        # Pasted blocks render as a compact indicator; the submitted text
        # (''.join(self._buffer)) always carries them verbatim.
        display = []

        for index, block in enumerate(self._buffer):
            if index in self._paste_blocks:
                display.append(self.term.bold_cyan(paste_block_indicator(block)))
            else:
                display.append(block)

        return ''.join(display)

    def _clear_rendered_lines(self) -> str:
        if self._rendered_lines <= 1:
            return '\r' + self.term.clear_eol()

        # The cursor sits at the end of the previous render's last row, so
        # clear that row, then climb one row at a time clearing each row
        # the old render occupied, ending on the block's first row ready
        # for the rewrite.
        clear = '\r' + self.term.clear_eol()
        climb = (self.term.cuu1 + '\r' + self.term.clear_eol()) * (self._rendered_lines - 1)
        return clear + climb

    def _visual_line_count(self, line: str) -> int:
        width = self.term.width

        if width <= 0:
            return 1

        return max(1, -(-self.term.length(line) // width))

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
