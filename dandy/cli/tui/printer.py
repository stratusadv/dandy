import random
import sys
import threading
from time import perf_counter, sleep
from typing import Callable, TypeVar

from blessed import Terminal

from dandy.cli.processing_phrases import PROCESSING_PHRASES
from dandy.cli.session import session
from dandy.cli.tui.ascii import DANDY_ASCII
from dandy.cli.tui.markdown import MarkdownRenderer
from dandy.cli.utils import get_cli_llm_config
from dandy.constants import __VERSION__
from dandy.llm.config import LlmConfig

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


class _StoryProgress:
    """Thread-safe accumulator for the story beats of a running task.

    The worker thread pushes beats (AI summary sentences or fallback labels)
    with `update`; the rendering thread prints settled beats in black and
    animates the newest one in blue with trailing dots.
    """

    def __init__(self, term: Terminal, step_indent: int = 2) -> None:
        self.term = term
        self.step_indent = step_indent
        self._beats: list[str] = ['Thinking']
        self._lock = threading.Lock()

    def update(self, beat: str) -> None:
        with self._lock:
            self._beats.append(beat)

    @property
    def beats(self) -> list[str]:
        with self._lock:
            return list(self._beats)

    def settled_frame(self, beat: str) -> str:
        indent = ' ' * ((self.step_indent * 2) + 1)
        return f'\r{self.term.normal}{indent}↳ {beat}{self.term.clear_eol()}\n'

    def frame(self, beat: str, dots: str) -> str:
        indent = ' ' * ((self.step_indent * 2) + 1)
        prefix = f'{self.term.bold_blue}{indent}↳ '
        max_beat_length = max(1, self.term.width - len(prefix) - 8)
        short_beat = beat if len(beat) <= max_beat_length else f'{beat[: max_beat_length - 1]}…'
        return f'\r{prefix}{short_beat} {dots}{self.term.clear_eol()}'


class Printer:
    def __init__(self, terminal: Terminal) -> None:
        self.term = terminal
        self.markdown_renderer = MarkdownRenderer(terminal)

    @staticmethod
    def blank_line():
        print(flush=True)

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

    def running_phrase(self, action_name: str):
        phrase = random.choice(PROCESSING_PHRASES)
        self.indented_event(text=f'{self.term.bold_blue}{phrase} in preparation of your request!')

    def start_task(self, action_name: str, task: str) -> float:
        self.indented_event(
            text=f'{self.term.bold_orange}{action_name}{self.term.normal} "{task}" ... ',
            indent=1,
            end='',
        )

        return perf_counter()

    def end_task(self, start_time: float, action_name: str = 'done'):
        print(
            f'{self.term.green}{action_name} {perf_counter() - start_time:.1f}s{self.term.normal}'
        )

    def run_timed_task(
        self, action_name: str, task: str, work: Callable[[Callable[[str], None]], T]
    ) -> T:
        """Run `work(update_beat)` while animating a story of AI summary beats.

        Prints a task header line, then a story: every beat pushed through
        `update_beat` is appended to the output, with the previous beats
        settling as plain lines and the most recent beat rendered in blue with
        animated trailing dots (so it is clear the task is still running). When
        `work` finishes, a completion sentence reports the total elapsed time.
        Rendering happens only on the calling thread (`work` runs on a daemon
        thread), and any exception raised by `work` is re-raised here.
        """
        start_time = perf_counter()

        self.indented_event(
            text=f'{self.term.bold_orange}{action_name}{self.term.normal} "{task}"', indent=1
        )

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
            sleep(0.12)

        for beat in progress.beats[settled_count:]:
            sys.stdout.write(progress.settled_frame(beat))

        if error_holder:
            raise error_holder[0]

        self.indented_event(
            text=(
                f'{self.term.bold_green}I have completed your request in '
                f'{format_verbose_duration(perf_counter() - start_time)}.'
            ),
            indent=2,
        )

        return result_holder['value']

    def indented_event(self, text: str, indent: int = 0, end: str = '\n'):
        print(
            f'{self.term.normal}{" " * ((indent * 2) + 1)}↳ {text}{self.term.normal}',
            end=end,
            flush=True,
        )

    def output(self, output: str):
        rendered_output = self.markdown_renderer.render(output)

        for line in rendered_output.splitlines():
            sleep(0.02)
            print(line)

    def error(self, error: str, description: str):
        self.indented_event(text=f'{self.term.red}Error: {self.term.normal}{error} !!!')
        self.red_divider()
        print(f'{description}')
