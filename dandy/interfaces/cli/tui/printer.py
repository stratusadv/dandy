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
from dandy.shared.settings.load import get_cli_llm_config
from dandy.infrastructure.llm.config import LlmConfig

T = TypeVar('T')

EVALUATING_LABEL = 'Evaluating'


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


class _StoryProgress:
    """Thread-safe accumulator for the story beats of a running task.

    The worker thread pushes `StoryBeat`s (AI summary sentences, tool action
    labels with their per-call detail, or plain notices) with `update`; the
    rendering thread prints them as a running list: consecutive tool beats
    with the same label share one heading line (the label in bold grey, or
    bold orange when the beat can mutate state), printed exactly once when
    the label appears and again when it reappears after a change, and each
    beat's description prints below it on its own line prefixed by the
    beat's ascii character (a bullet when the beat carries none). File paths
    in a tool beat's description are emitted as clickable file:// links.
    Non-tool beats (narration in bold blue, system notices plain) print with
    no prefix. The newest beat animates with a bold orange 'Evaluating ...'
    suffix. Every line is flush left. The animating frame
    folds a multi-line beat onto one line so its per-tick redraw stays on a
    single line; the settled frame prints the beat's text in full.
    """

    def __init__(self, term: Terminal) -> None:
        self.term = term
        self._beats: list[StoryBeat] = [StoryBeat(description=random.choice(THINKING_PHRASES))]
        self._lock = threading.Lock()
        self._heading_beat: StoryBeat | None = None
        self._heading_emitted: set[int] = set()

    def update(self, beat: StoryBeat) -> None:
        with self._lock:
            self._beats.append(beat)

    @property
    def beats(self) -> list[StoryBeat]:
        with self._lock:
            return list(self._beats)

    def _previous_tool_label(self, beat: StoryBeat) -> str:
        beats = self.beats

        for index, current in enumerate(beats):
            if current is beat:
                for earlier in reversed(beats[:index]):
                    if earlier.label:
                        return earlier.label

                break

        return ''

    def _needs_heading(self, beat: StoryBeat) -> bool:
        return bool(beat.label) and beat.label != self._previous_tool_label(beat)

    def _styled_label(self, beat: StoryBeat) -> str:
        label_style = self.term.bold_orange if beat.can_mutate_state else self.term.bold_grey

        return f'{label_style}{beat.label}{self.term.normal}'

    def _styled_description(self, beat: StoryBeat, description: str) -> str:
        if beat.label:
            return linkify_file_paths(description)

        if beat.kind == 'narration':
            return f'{self.term.bold_blue}{description}{self.term.normal}'

        return description

    def _emit_heading(self, beat: StoryBeat) -> str:
        if not self._needs_heading(beat) or id(beat) in self._heading_emitted:
            return ''

        self._heading_beat = beat
        self._heading_emitted.add(id(beat))

        return f'{self.term.normal}{self._styled_label(beat)}{self.term.clear_eol()}\n'

    def settled_frame(self, beat: StoryBeat) -> str:
        heading = self._emit_heading(beat)
        description = self._styled_description(beat, beat.description)

        if beat.label:
            line = f'{self.term.normal}{beat.ascii_char or "•"} {description}'
        else:
            line = f'{self.term.normal}{description}'

        return f'\r{heading}{line}{self.term.clear_eol()}\n'

    def frame(self, beat: StoryBeat, dots: str) -> str:
        heading = ''

        if self._heading_beat is not beat:
            heading = self._emit_heading(beat)
            self._heading_beat = beat

        prefix = f'{self.term.normal}{beat.ascii_char or "•"} ' if beat.label else self.term.normal
        plain_description = ' '.join(beat.description.split())
        max_beat_length = max(1, self.term.width - len(prefix) - len(f'{EVALUATING_LABEL} ...'))

        if len(plain_description) > max_beat_length:
            description_part = plain_description[: max_beat_length - 1]
        else:
            description_part = plain_description

        beat_text = self._styled_description(beat, description_part)
        beat_line = f'{prefix}{beat_text}'

        if beat_text:
            beat_line = f'{beat_line} '

        suffix = f'{self.term.bold_orange}{EVALUATING_LABEL} {dots}{self.term.normal}'

        return f'\r{heading}{beat_line}{suffix}{self.term.clear_eol()}'


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

    def running_phrase(self):
        phrase = random.choice(THINKING_PHRASES)
        self.event(text=f'{self.term.bold_blue}{phrase} in preparation of your request!')

    def run_timed_task(
        self,
        action_name: str,
        task: str,
        work: Callable[[Callable[[StoryBeat], None]], T],
        stop_signal: StopSignal | None = None,
    ) -> T:
        """Run `work(update_beat)` while animating a story of AI summary beats.

        Prints a task header line, then a story: every `StoryBeat` pushed
        through `update_beat` is appended to the output as a running list.
        Consecutive tool beats with the same label settle under one heading
        line (the label in grey, bold orange when the beat can mutate state)
        with each description on its own bulleted line; non-tool beats settle
        as plain lines; the most recent beat is rendered with a bold orange
        animated 'Evaluating ...' suffix (so it is clear the task is still
        running). When `work` finishes, a completion sentence reports the
        total elapsed time. Rendering happens only on the
        calling thread (`work` runs on a daemon thread), and any exception
        raised by `work` is re-raised here.

        While the task runs, keys are polled (in cbreak mode) so the user can
        press escape twice to stop the run: on the second consecutive escape
        `stop_signal` is set and a one-line notice is printed. Any other key
        resets the escape count, matching the prompt's double-escape rule.
        """
        start_time = perf_counter()

        self.event(text=f'{self.term.bold_orange}{action_name}{self.term.normal} "{task}"')

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
        dots = 1
        escape_count = 0

        with self.term.cbreak():
            while thread.is_alive():
                beats = progress.beats

                if len(beats) > settled_count + 1:
                    for beat in beats[settled_count:-1]:
                        sys.stdout.write(progress.settled_frame(beat))
                    settled_count = len(beats) - 1
                    dots = 1

                sys.stdout.write(progress.frame(beats[-1], '.' * dots))
                sys.stdout.flush()

                dots = (dots % 3) + 1

                if stop_signal is not None:
                    escape_count = self._poll_for_stop(stop_signal, escape_count)

                sleep(0.12)

        for beat in progress.beats[settled_count:]:
            sys.stdout.write(progress.settled_frame(beat))

        if error_holder:
            raise error_holder[0]

        self.event(
            text=(
                f'{self.term.bold_green}I have completed your request in '
                f'{format_verbose_duration(perf_counter() - start_time)}.'
            )
        )

        return result_holder['value']

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
        self.event(text=f'{self.term.red}Error: {self.term.normal}{error} !!!')
        self.red_divider()
        print(f'{description}')
