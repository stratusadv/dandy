import random
import re
import sys
import threading
from pathlib import Path
from time import perf_counter, sleep
from typing import Callable, TypeVar

from blessed import Terminal

from dandy.interfaces.cli.thinking_phrases import THINKING_PHRASES
from dandy.application.agent.session import session
from dandy.application.agent.session_store import SessionStore
from dandy.interfaces.cli.tui.ascii import DANDY_ASCII
from dandy.interfaces.cli.tui.markdown import MarkdownRenderer
from dandy.domain.tool.beat import StoryBeat
from dandy.shared.cancellation import StopSignal
from dandy.shared.constants import AGENTS_MD_FILE_NAME, __VERSION__
from dandy.shared.interaction import QuestionGate
from dandy.shared.settings.load import get_cli_llm_config
from dandy.infrastructure.llm.config import LlmConfig

T = TypeVar('T')


def format_verbose_duration(seconds: float) -> str:
    """Humanize an elapsed duration for the completion sentence."""
    seconds = max(0.0, seconds)

    if seconds < 60:
        return f'{seconds:.1f} seconds'

    total_seconds = round(seconds)
    minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts: list[str] = []

    if hours:
        parts.append(f'{hours} hour{"s" if hours != 1 else ""}')

    if minutes:
        parts.append(f'{minutes} minute{"s" if minutes != 1 else ""}')

    if secs:
        parts.append(f'{secs} second{"s" if secs != 1 else ""}')

    return ''.join(parts) if len(parts) == 1 else ' and '.join(parts)


_PATH_WORD_RE = re.compile(r'[A-Za-z0-9._~/-]+')
_FILE_EXTENSION_RE = re.compile(r'\.[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*$')


def _is_path_token(word: str) -> bool:
    if not _PATH_WORD_RE.fullmatch(word):
        return False

    if word in ('.', '..') or word.startswith('-'):
        return False

    return '/' in word or bool(_FILE_EXTENSION_RE.search(word))


def linkify_file_paths(description: str) -> str:
    """Wrap the file paths in a beat's description in clickable OSC 8 links.

    A whitespace-separated word is linked when it uses only path-safe
    characters, is not a dash flag or `.`/`..`, and either contains a `/` or
    ends in a dotted extension with a letter (so `src/foo.py` links while
    `lines`, `1-10`, `-q`, and `1.0.5` do not). Relative paths resolve against
    the session's project base path. The sequences are raw OSC 8 because
    blessed's `hyperlink` terminfo capability is unavailable.
    """

    def linkify(word_match: re.Match[str]) -> str:
        word = word_match.group(0)

        if not _is_path_token(word):
            return word

        path = Path(word).expanduser()

        if not path.is_absolute():
            path = session.project_base_path / path

        return f'\x1b]8;;{path.as_uri()}\x1b\\{word}\x1b]8;;\x1b\\'

    return re.sub(r'\S+', linkify, description)


EVALUATING_PHRASE_CHANGE_SECONDS = 3.0


class _StoryProgress:
    """Thread-safe accumulator for the story beats of a running task.

    The worker thread pushes `StoryBeat`s (AI summary sentences, tool action
    labels with their per-call detail, or plain notices) with `update`; the
    rendering thread prints them as a running list: consecutive tool beats
    with the same label share one heading line (the label in bold skyblue, or
    bold orange when the beat can mutate state), printed once when the label
    appears and again whenever the label changes or a non-tool line (a
    thought or a notice) has printed in between, and each beat's description
    prints below it on its own line prefixed by a `↳` arrow colored like
    the label. Each heading, and each narration, is preceded by a blank
    line. File paths in a tool beat's description are emitted as clickable
    file:// links. Non-tool beats (narration in bold blue, compaction
    notices in bold purple, system notices plain) print with no prefix.
    The newest beat animates with a bold blue thinking-phrase line below
    it: a random phrase is drawn once and held for
    `EVALUATING_PHRASE_CHANGE_SECONDS`, and the region is redrawn in place
    every tick. Every line is flush left.
    The animating frame folds a multi-line description onto the single line
    above the phrase line; the settled frame prints the beat's text in full,
    clearing every line it overwrites so no tail of the longer animating
    frame survives. The leftover phrase line is not deleted but reused as
    the first line of the next region, so beats within a group settle with
    no blank line between them.
    """

    def __init__(self, term: Terminal) -> None:
        self.term = term
        self._beats: list[StoryBeat] = []
        self._lock = threading.Lock()
        self._heading_beat: StoryBeat | None = None
        self._heading_emitted: set[int] = set()
        self._evaluating_phrase: str | None = None
        self._evaluating_phrase_since: float = 0.0
        self._live_frame: bool = False
        self._live_lines: int = 0
        self._live_desc_index: int = 1
        self._carry_lines: int = 0

    def update(self, beat: StoryBeat) -> None:
        with self._lock:
            self._beats.append(beat)

    @property
    def beats(self) -> list[StoryBeat]:
        with self._lock:
            return list(self._beats)

    def _needs_heading(self, beat: StoryBeat) -> bool:
        if not beat.label:
            return False

        beats = self.beats

        for index, current in enumerate(beats):
            if current is beat:
                if index == 0:
                    return True

                earlier = beats[index - 1]

                return not earlier.label or earlier.label != beat.label

        return True

    def _label_style(self, beat: StoryBeat) -> str:
        return self.term.bold_orange if beat.can_mutate_state else self.term.bold_skyblue

    def _styled_label(self, beat: StoryBeat) -> str:
        return f'\n{self._label_style(beat)}{beat.label}{self.term.normal}'

    def _styled_description(self, beat: StoryBeat, description: str) -> str:
        if beat.label:
            return linkify_file_paths(description)

        if beat.kind == 'narration':
            return f'\n{self.term.bold_blue}{description}{self.term.normal}'

        if beat.kind == 'compaction':
            return f'\n{self.term.bold_purple}{description}{self.term.normal}'

        return description

    def _emit_heading(self, beat: StoryBeat) -> str:
        if not self._needs_heading(beat) or id(beat) in self._heading_emitted:
            return ''

        self._heading_beat = beat
        self._heading_emitted.add(id(beat))

        # A bare LF keeps the cursor's column, so the description line below
        # the heading gets an explicit CR back to column zero.
        return f'{self.term.normal}{self._styled_label(beat)}{self.term.clear_eol()}\n\r'

    def _rotating_evaluating_phrase(self) -> str:
        """The current thinking phrase, re-drawn at most every 3 seconds."""
        now = perf_counter()

        if (
            self._evaluating_phrase is None
            or now - self._evaluating_phrase_since >= EVALUATING_PHRASE_CHANGE_SECONDS
        ):
            self._evaluating_phrase = random.choice(THINKING_PHRASES)
            self._evaluating_phrase_since = now

        return self._evaluating_phrase

    def drop_live_frame(self) -> None:
        """Forget the live frame so the next write starts on a fresh line."""
        self._live_frame = False
        self._live_lines = 0
        self._live_desc_index = 1
        self._carry_lines = 0

    def _fresh_line_prefix(self) -> str:
        carry = self._carry_lines
        self._carry_lines = 0
        return f'\x1b[{carry}A\r' if carry else '\r'

    def pause_at_fresh_line(self) -> str:
        """Stop the animation and land on a fresh line at column zero.

        Settles the newest beat while it still animates, then moves the
        cursor onto the leftover phrase line; used before a question prompt
        that must not share a line with the animating frame.
        """
        if not self._live_frame:
            return self._fresh_line_prefix()

        with self._lock:
            beats = list(self._beats)

        if not beats:
            return ''

        return self.settled_frame(beats[-1]) + self._fresh_line_prefix()

    def carry_prefix(self) -> str:
        """The cursor move onto a leftover carry line, or '' when there is none."""
        if not self._carry_lines:
            return ''

        return self._fresh_line_prefix()

    def _clear_line_tails(self, text: str) -> str:
        """Clear to the end of every line of `text` except the last.

        A settled multi-line description overwrites the live region line by
        line; without a clear per line, a longer old line would leave its
        tail visible behind the shorter new line.
        """
        parts = text.split('\n')

        for index in range(len(parts) - 1):
            parts[index] = f'{parts[index]}{self.term.clear_eol()}'

        return '\n'.join(parts)

    def settled_frame(self, beat: StoryBeat) -> str:
        heading = self._emit_heading(beat)
        description = self._styled_description(beat, beat.description)

        if beat.label:
            line = f'{self._label_style(beat)}↳{self.term.normal} {description}'
        else:
            line = f'{self.term.normal}{description}'

        # A bare LF keeps the cursor's column, so every line of a multi-line
        # description gets an explicit CR back to column zero.
        line = line.replace('\n', '\n\r')
        content = f'{heading}{line}'

        if not self._live_frame:
            return f'{self._fresh_line_prefix()}{content}{self.term.clear_eol()}\n\r'

        live_lines = self._live_lines
        desc_index = self._live_desc_index
        self._live_frame = False
        self._live_lines = 0
        self._live_desc_index = 1

        if description.startswith('\n'):
            # A narration region starts with a blank line; settle from the
            # region start so the content's leading newline lands the text
            # on its own line, and clear the stale start line.
            move_up = f'\x1b[{live_lines - 1}A\r{self.term.clear_eol()}'
            leftover_lines = max(0, live_lines - (content.count('\n') + 1))
        else:
            move_up = f'\x1b[{live_lines - desc_index}A\r'
            leftover_lines = max(0, (live_lines - desc_index + 1) - (content.count('\n') + 1))

        self._carry_lines = leftover_lines
        clear_leftover = f'{self.term.clear_eol()}\n\r' * leftover_lines

        return (
            f'{move_up}{self._clear_line_tails(content)}{self.term.clear_eol()}\n\r{clear_leftover}'
        )

    def frame(self, beat: StoryBeat) -> str:
        phrase = self._rotating_evaluating_phrase()
        heading = ''

        if self._heading_beat is not beat:
            heading = self._emit_heading(beat)
            self._heading_beat = beat

        prefix = (
            f'{self._label_style(beat)}↳{self.term.normal} ' if beat.label else self.term.normal
        )
        plain_description = ' '.join(beat.description.split())
        max_beat_length = max(1, self.term.width - len(prefix) - 1)

        if len(plain_description) > max_beat_length:
            description_part = plain_description[: max_beat_length - 1]
        else:
            description_part = plain_description

        beat_text = self._styled_description(beat, description_part)
        beat_line = f'{prefix}{beat_text}'
        evaluating_line = f'{self.term.bold_blue}{phrase}{self.term.normal}'

        if self._live_frame:
            # A narration region's own text begins with a leading newline,
            # so a redraw must return to the region's start line; every
            # other region is re-drawn from its description line.
            up_lines = (
                self._live_lines - 1
                if beat_text.startswith('\n')
                else self._live_lines - self._live_desc_index
            )
            line_prefix = f'\x1b[{up_lines}A\r'
        else:
            line_prefix = self._fresh_line_prefix()
            # Redraws keep the region's layout; only a fresh frame can add a
            # heading line or a leading blank line (narration) above the
            # description line. A carry line only moves where the region
            # starts, not how tall it is.
            self._live_desc_index = (
                1 + (1 if heading else 0) + (1 if beat_text.startswith('\n') else 0)
            )
            self._live_lines = self._live_desc_index + 1

        frame_str = (
            f'{line_prefix}{heading}{beat_line}{self.term.clear_eol()}\n\r'
            f'{evaluating_line}{self.term.clear_eol()}'
        )

        self._live_frame = True

        return frame_str


def agents_md_banner_line(project_base_path: Path) -> str:
    """The welcome banner line summarizing the project's AGENTS.md."""
    agents_md_path = Path(project_base_path, AGENTS_MD_FILE_NAME)

    if not agents_md_path.is_file():
        return 'not found - run /init to create one'

    size_bytes = agents_md_path.stat().st_size

    if size_bytes >= 1024:
        return f'found ({size_bytes / 1024:.1f} KB) - loaded into the agent system prompt'

    return f'found ({size_bytes} bytes) - loaded into the agent system prompt'


def session_banner_line(store: SessionStore) -> str:
    """The welcome banner line summarizing the project's saved sessions."""
    latest_name = store.latest()

    if latest_name is None:
        return 'none yet - the first turn is saved automatically'

    session_count = len(store.list_sessions())

    return f'{session_count} saved, latest: {latest_name} - resume it with /resume {latest_name}'


class Printer:
    def __init__(self, terminal: Terminal) -> None:
        self.term = terminal
        self.markdown_renderer = MarkdownRenderer(terminal)

    def blue_divider(self):
        print(self.term.bold_blue('─' * self.term.width), flush=True)

    def purple_divider(self):
        print(self.term.bold_purple('─' * self.term.width), flush=True)

    def divider(self):
        print(self.term.bold_grey('─' * self.term.width), flush=True)

    def grey_divider(self):
        print(self.term.bold_grey('─' * self.term.width), flush=True)

    def green_divider(self):
        print(self.term.bold_green('─' * self.term.width), flush=True)

    def red_divider(self):
        print(self.term.bold_red('─' * self.term.width), flush=True)

    def welcome(self):
        print(self.term.bold_blue(f'\n{DANDY_ASCII}\n'))
        self.blue_divider()
        print(self.term.bold_blue('Version      : ') + __VERSION__)
        print(
            self.term.bold_blue('Model        : ') + LlmConfig(get_cli_llm_config('CODING')).model
        )
        print(self.term.bold_blue('Project Dir  : ') + str(session.project_base_path))
        print(
            self.term.bold_blue('AGENTS.md    : ')
            + agents_md_banner_line(session.project_base_path)
        )
        print(
            self.term.bold_blue('Sessions     : ')
            + session_banner_line(SessionStore.for_project(session.project_base_path))
        )

    def run_timed_task(
        self,
        task: str,
        work: Callable[[Callable[[StoryBeat], None]], T],
        stop_signal: StopSignal | None = None,
        question_gate: QuestionGate | None = None,
        question_handler: Callable[[str, list[str]], str | None] | None = None,
    ) -> T:
        """Run `work(update_beat)` while animating a story of AI summary beats.

        Prints a task header line, then a story: every `StoryBeat` pushed
        through `update_beat` is appended to the output as a running list.
        Consecutive tool beats with the same label settle under one heading
        line (the label in bold skyblue, bold orange when the beat can mutate
        state),
        re-printed whenever the label changes or a non-tool line settles in
        between, with each description on its own line prefixed by a `↳` in
        the label's color; non-tool beats settle as plain lines; the most
        recent beat is rendered with a bold blue thinking-phrase line
        below it (a random phrase held for 3 seconds, so it is clear the
        task is still running). When `work`
        finishes, a completion sentence reports the total elapsed time.
        Rendering happens only on the
        calling thread (`work` runs on a daemon thread), and any exception
        raised by `work` is re-raised here.

        While the task runs, keys are polled (in cbreak mode) so the user can
        press escape twice to stop the run: on the second consecutive escape
        `stop_signal` is set and a one-line notice is printed. Any other key
        resets the escape count, matching the prompt's double-escape rule.

        When a `question_gate` is given, a question the worker parks there
        pauses the animation: the calling thread (the only one allowed to
        touch the terminal) settles every beat the render loop has not
        printed yet, moves the cursor onto the leftover phrase line so the
        prompt prints at column zero, then calls `question_handler(question,
        choices)` and delivers its result to the gate, dropping the live
        frame afterwards so the resumed animation starts on a fresh line. A
        `None` result means the user stopped the run (the gate then sets the
        stop signal and answers the worker with a stop sentinel).
        """
        start_time = perf_counter()

        self.event(text=f'{self.term.bold_orange}"{task}"{self.term.normal}')

        progress = _StoryProgress(self.term)
        result_holder: dict[str, T] = {}
        error_holder: list[Exception] = []

        def runner() -> None:
            try:
                result_holder['value'] = work(progress.update)
            except Exception as error:
                error_holder.append(error)

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        settled_count = 0
        escape_count = 0

        while True:
            with self.term.cbreak():
                while thread.is_alive() and not self._has_pending_question(question_gate):
                    beats = progress.beats

                    if len(beats) > settled_count + 1:
                        for beat in beats[settled_count:-1]:
                            sys.stdout.write(progress.settled_frame(beat))
                        settled_count = len(beats) - 1

                    if len(beats) > settled_count:
                        # A settled beat (e.g. settled by a question pause)
                        # must not be re-animated: only the last unsettled
                        # beat animates.
                        sys.stdout.write(progress.frame(beats[-1]))
                        sys.stdout.flush()

                    if stop_signal is not None:
                        escape_count = self._poll_for_stop(stop_signal, escape_count)

                    sleep(0.12)

            if not thread.is_alive():
                break

            pending_question = question_gate.pending

            if pending_question is None or question_handler is None:
                break

            for beat in progress.beats[settled_count:]:
                sys.stdout.write(progress.settled_frame(beat))

            sys.stdout.write(progress.pause_at_fresh_line())
            sys.stdout.flush()
            settled_count = len(progress.beats)
            answer = question_handler(pending_question.question, pending_question.choices)
            question_gate.deliver(answer)
            progress.drop_live_frame()

        for beat in progress.beats[settled_count:]:
            sys.stdout.write(progress.settled_frame(beat))

        carry = progress.carry_prefix()

        if carry:
            sys.stdout.write(carry)
            sys.stdout.flush()

        if error_holder:
            raise error_holder[0]

        self.event(
            text=(
                '\n'
                f'{self.term.bold_green}Request Completed in '
                f'{format_verbose_duration(perf_counter() - start_time)}'
            )
        )

        return result_holder['value']

    @staticmethod
    def _has_pending_question(question_gate: QuestionGate | None) -> bool:
        return question_gate is not None and question_gate.pending is not None

    def _poll_for_stop(self, stop_signal: StopSignal, escape_count: int) -> int:
        """Poll for a double-escape while a task runs; return the new count.

        Reads one key with a zero timeout (so the render loop never blocks on
        input). Two consecutive escape presses set `stop_signal` and print a
        notice; any other key resets the count. Returns the updated escape
        count. Safe on non-TTY stdin: when no key can be read, the count is
        returned unchanged.
        """
        try:
            key = self.term.inkey(timeout=0)
        except Exception:
            return escape_count

        if not key:
            return escape_count

        key_text = str(key)

        # blessed may deliver two escapes pressed in quick succession as a
        # single keystroke ('\\x1b\\x1b'), so count every escape byte. Other
        # sequences (arrows, etc.) contain extra bytes and never count.
        if key_text and key_text.strip('\x1b') == '':
            escape_count += key_text.count('\x1b')

            if escape_count >= 2:
                stop_signal.set()
                print(f'{self.term.yellow}Stopping...{self.term.normal}', flush=True)

            return escape_count

        return 0

    def event(self, text: str, end: str = '\n'):
        print(f'{self.term.normal}{text}{self.term.normal}', end=end, flush=True)

    def output(self, output: str):
        rendered_output = self.markdown_renderer.render(output)

        for line in rendered_output.splitlines():
            sleep(0.02)
            print(line)

    def edited_files(self, paths: list[str]) -> None:
        """Print the turn's edited-file list above the final answer.

        A bold grey 'Edited files:' heading followed by one bulleted,
        clickable file:// link per path; prints nothing when the list is
        empty.
        """
        if not paths:
            return

        print(f'{self.term.bold_grey}Edited files:{self.term.normal}')

        for path in paths:
            print(f'{self.term.normal}• {linkify_file_paths(path)}')

    def error(self, error: str, description: str):
        self.event(text=f'\n{self.term.red}Error: {self.term.normal}{error} !!!')
        self.red_divider()
        print(f'{description}')
