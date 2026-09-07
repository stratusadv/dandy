import random
import sys
import threading
from time import perf_counter, sleep, time
from typing import Callable

from blessed import Terminal

from dandy.cli.processing_phrases import PROCESSING_PHRASES
from dandy.cli.session import session
from dandy.cli.tui.ascii import DANDY_ASCII
from dandy.cli.tui.tools import wrap_text_with_indentation
from dandy.cli.utils import get_cli_llm_config
from dandy.constants import __VERSION__
from dandy.llm.config import LlmConfig


class _TaskProgress:
    """Thread-safe holder for the label of the currently running task step.

    The worker thread pushes labels with `update`; the rendering thread reads
    `current_label` to draw one animated line per label.
    """

    def __init__(self, term: Terminal, step_indent: int = 2) -> None:
        self.term = term
        self.step_indent = step_indent
        self._label = 'Thinking'
        self._lock = threading.Lock()

    def update(self, label: str) -> None:
        with self._lock:
            self._label = label

    @property
    def current_label(self) -> str:
        with self._lock:
            return self._label

    def frame(self, label: str, dots: str) -> str:
        indent = ' ' * ((self.step_indent * 2) + 1)
        prefix = f'{self.term.normal}{indent}↳ '
        max_label_length = max(1, self.term.width - len(prefix) - 8)
        short_label = (
            label if len(label) <= max_label_length else f'{label[: max_label_length - 1]}…'
        )
        return f'\r{prefix}{short_label} {dots}{self.term.clear_eol()}'

    def completed_frame(self, label: str, duration: float) -> str:
        indent = ' ' * ((self.step_indent * 2) + 1)
        return (
            f'\r{indent}↳ {label} {self.term.green}took {duration:.1f}s'
            f'{self.term.normal}{self.term.clear_eol()}'
        )


class Printer:
    def __init__(self, terminal: Terminal) -> None:
        self.term = terminal

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
        self, action_name: str, task: str, work: Callable[[Callable[[str], None]], object]
    ) -> object:
        """Run `work(update_label)` while animating the current step's '...'.

        Prints a task header line, then one line per step label pushed through
        `update_label`. The trailing dots alternate while the step is running
        so it is clear the task is still going on. Rendering happens only on
        the calling thread (`work` runs on a daemon thread), and any exception
        raised by `work` is re-raised here. Each step finishes with a green
        `label took N.Ns` so completed steps are visible before the next one
        starts. `action_name` and `task` name the header line; `work` receives
        `update_label` to report each step it is working on and returns the
        final result.
        """
        start_time = perf_counter()

        self.indented_event(
            text=f'{self.term.bold_orange}{action_name}{self.term.normal} "{task}"', indent=1
        )

        progress = _TaskProgress(self.term)
        result_holder = {}

        def runner() -> None:
            try:
                result_holder['value'] = work(progress.update)
            except Exception as error:
                result_holder['error'] = error

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        rendered_label = None
        label_start_time = 0.0
        dots = 1

        while thread.is_alive():
            label = progress.current_label

            if label != rendered_label:
                if rendered_label is not None:
                    print(
                        progress.completed_frame(rendered_label, perf_counter() - label_start_time)
                    )
                rendered_label = label
                label_start_time = perf_counter()
                dots = 1

            sys.stdout.write(progress.frame(label, '.' * dots))
            sys.stdout.flush()

            dots = (dots % 3) + 1
            sleep(0.12)

        if rendered_label is not None:
            print(progress.completed_frame(rendered_label, perf_counter() - label_start_time))

        if 'error' in result_holder:
            raise result_holder['error']

        self.indented_event(
            text=f'{self.term.bold_green}Done in {perf_counter() - start_time:.1f}s', indent=2
        )

        return result_holder['value']

    def indented_event(self, text: str, indent: int = 0, end: str = '\n'):
        print(
            f'{self.term.normal}{" " * ((indent * 2) + 1)}↳ {text}{self.term.normal}',
            end=end,
            flush=True,
        )

    def output(self, output: str):
        wrapped_output = wrap_text_with_indentation(output, self.term.width)

        for line in wrapped_output.splitlines():
            sleep(0.02)
            print(line)

    def error(self, error: str, description: str):
        self.indented_event(text=f'{self.term.red}Error: {self.term.normal}{error} !!!')
        self.red_divider()
        print(f'{description}')
