import sys
import threading
from time import perf_counter, sleep
from typing import Callable, TypeVar

from blessed import Terminal

from dandy.application.agent.session import session
from dandy.application.agent.session_store import SessionStore
from dandy.domain.tool.beat import StoryBeat
from dandy.shared.cancellation import StopSignal
from dandy.shared.constants import __VERSION__
from dandy.shared.interaction import QuestionGate
from dandy.shared.settings.load import get_cli_llm_config
from dandy.infrastructure.llm.config import LlmConfig
from dandy.interfaces.cli.tui.ascii import DANDY_ASCII
from dandy.interfaces.cli.tui.banner import (
    agents_md_banner_line,
    format_verbose_duration,
    session_banner_line,
)
from dandy.interfaces.cli.tui.markdown import MarkdownRenderer
from dandy.interfaces.cli.tui.story_progress import StoryProgress
from dandy.interfaces.cli.tui.text import linkify_file_paths

T = TypeVar('T')


class Printer:
    def __init__(self, terminal: Terminal) -> None:
        self.term = terminal
        self.markdown_renderer = MarkdownRenderer(terminal)

    def bold_blue_divider(self):
        print(self.term.bold_blue('─' * self.term.width), flush=True)

    def blue_divider(self):
        print(self.term.blue('─' * self.term.width), flush=True)

    def purple_divider(self):
        print(self.term.purple('─' * self.term.width), flush=True)

    def bold_grey_divider(self):
        print(self.term.bold_grey('─' * self.term.width), flush=True)

    def bold_green_divider(self):
        print(self.term.bold_green('─' * self.term.width), flush=True)

    def bold_red_divider(self):
        print(self.term.bold_red('─' * self.term.width), flush=True)

    def welcome(self):
        print(self.term.bold_blue(f'\n{DANDY_ASCII}\n'))
        self.bold_blue_divider()
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

        progress = StoryProgress(self.term)
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

    def file_change_sections(
        self, added_files: list[str], modified_files: list[str], removed_files: list[str]
    ) -> None:
        """Print the turn's file sections below the final answer.

        One section per non-empty action, in the order Added Files, Modified
        Files, Removed Files: a bold blue title, a thin blue bottom border,
        one line per path with the action-colored bullet (green added, blue
        modified, red removed) beside a clickable file:// link, and an empty
        line before each section; prints nothing when every list is empty.
        """
        sections = (
            ('Added Files', added_files, self.term.green),
            ('Modified Files', modified_files, self.term.blue),
            ('Removed Files', removed_files, self.term.red),
        )

        for title, paths, bullet_style in sections:
            if not paths:
                continue

            print()
            print(f'{self.term.bold_blue}{title}{self.term.normal}')
            print(self.term.blue('─' * self.term.width))

            for path in paths:
                print(
                    f'{self.term.normal}{bullet_style}•{self.term.normal} '
                    f'{linkify_file_paths(path)}'
                )

    def error(self, error: str, description: str):
        self.event(text=f'\n{self.term.red}Error: {self.term.normal}{error} !!!')
        self.bold_red_divider()
        print(f'{description}')
