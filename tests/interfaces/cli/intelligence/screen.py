class MiniScreen:
    """A minimal VT emulator for asserting what a Tui write sequence shows on screen.

    Supports the sequences the Tui emits: printable text, CR, LF (with scroll,
    returning to the left margin as real terminals do),
    CSI K (clear to end of line), CSI A/B/C/D (relative cursor movement),
    and CSI m (SGR, ignored). A full line wraps on the next character or line
    break (delayed wrap, like xterm). Other CSI sequences (device status
    queries, mode reports) are consumed and ignored, matching a real terminal,
    as are DCS/OSC/SOS/PM string sequences (blessed emits kitty-keyboard and
    color queries on startup, and a real terminal never prints their
    payloads).
    `char_widths` maps characters to rendered column widths, so tests can
    simulate a terminal whose font renders a character (e.g. the prompt
    bullet) wider or narrower than the Tui's own measurement.
    """

    def __init__(
        self, width: int = 80, height: int = 24, char_widths: dict[str, int] | None = None
    ) -> None:
        self.width = width
        self.height = height
        self.char_widths = char_widths or {}
        self.lines = [[' '] * width for _ in range(height)]
        self.row = 0
        self.col = 0

    def feed(self, data: str) -> None:
        index = 0
        size = len(data)

        while index < size:
            char = data[index]

            if char == '\x1b' and data.startswith('\x1b[', index):
                index = self._feed_csi(data, index + 2)
            elif char == '\x1b' and data[index + 1] in 'P]^X':
                index = self._feed_string(data, index)
            elif char == '\r':
                self.col = 0
                index += 1
            elif char == '\n':
                self._line_feed()
                index += 1
            else:
                self._put(char)
                index += 1

    def _feed_string(self, data: str, index: int) -> int:
        terminator = data.find('\x1b\\', index + 2)

        if data[index + 1] == ']':
            bell = data.find('\x07', index + 2)

            if bell != -1 and (terminator == -1 or bell < terminator):
                return bell + 1

        return len(data) if terminator == -1 else terminator + 2

    def _feed_csi(self, data: str, index: int) -> int:
        final_index = index

        while final_index < len(data) and not '\x40' <= data[final_index] <= '\x7e':
            final_index += 1

        if final_index >= len(data):
            return len(data)

        params = data[index:final_index]
        final = data[final_index]
        digits = ''.join(char for char in params if char.isdigit())
        amount = int(digits) if digits else 1

        if final == 'K':
            for column in range(self.col, self.width):
                self.lines[self.row][column] = ' '
        elif final == 'A':
            self.row = max(0, self.row - amount)
        elif final == 'B':
            self.row = min(self.height - 1, self.row + amount)
        elif final == 'C':
            self.col = min(self.width - 1, self.col + amount)
        elif final == 'D':
            self.col = max(0, self.col - amount)

        return final_index + 1

    def _put(self, char: str) -> None:
        if self.col >= self.width:
            # the line is full and the wrap is pending: real terminals move
            # down only once, whether the next event is a character or a
            # line break
            self._line_feed()

        width = self.char_widths.get(char, 1)

        self.lines[self.row][self.col] = char

        for offset in range(1, width):
            if self.col + offset < self.width:
                self.lines[self.row][self.col + offset] = ' '

        self.col += width

    def _line_feed(self) -> None:
        self.row += 1
        self.col = 0

        if self.row >= self.height:
            del self.lines[0]
            self.lines.append([' '] * self.width)
            self.row = self.height - 1

    def line(self, row: int) -> str:
        return ''.join(self.lines[row]).rstrip()

    def row_starting_with(self, text: str) -> int:
        for row in range(self.height):
            if self.line(row).startswith(text):
                return row

        message = f'no line starts with {text!r}'
        raise ValueError(message)

    def text(self) -> str:
        return '\n'.join(self.line(row) for row in range(self.height)).rstrip('\n')


class ScreenStdout:
    """A stdout stand-in that feeds every write into a MiniScreen."""

    def __init__(self, screen: MiniScreen) -> None:
        self.screen = screen

    def write(self, data: str) -> int:
        self.screen.feed(data)
        return len(data)

    def flush(self) -> None:
        pass
