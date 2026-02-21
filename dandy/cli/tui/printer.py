import random
from time import sleep, time

from blessed import Terminal

from dandy import constants
from dandy.cli.actions.action import BaseAction
from dandy.cli.constants import PROCESSING_PHRASES
from dandy.cli.session import session
from dandy.cli.tui.ascii import DANDY_ANSII
from dandy.cli.tui.tools import wrap_text_with_indentation
from dandy.llm.config import LlmConfig


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
        print('─' * self.term.width, flush=True)

    def green_divider(self):
        print(self.term.bold_green('─' * self.term.width), flush=True)

    def red_divider(self):
        print(self.term.bold_red('─' * self.term.width), flush=True)

    def welcome(self):
        print(self.term.bold_blue(f'\n{DANDY_ANSII}'))
        self.blue_divider()
        print(self.term.bold_blue('Version      : ') + constants.__VERSION__)
        print(self.term.bold_blue('Model        : ') + LlmConfig('DEFAULT').model)
        print(self.term.bold_blue('Project Dir  : ') + str(session.project_base_path))

    def running_action(self, action: BaseAction):
        phrase = random.choice(PROCESSING_PHRASES)
        self.indented_event(
            text=f'{self.term.bold_blue}{phrase} in preparation of "{action.name_gerund}" ',
        )

    def completed_action(self, start_time: float, action: BaseAction):
        self.indented_event(
            text=f'{self.term.bold_green}Finished in only {time() - start_time:.1f}s',
            indent=1
        )

    def start_task(self, action_name: str, task: str) -> float:
        self.indented_event(
            text=f'{self.term.bold_orange}{action_name}{self.term.normal} "{task}" ... ',
            indent=1,
            end='',
        )
        return time()

    def end_task(self, start_time: float, action_name: str = 'done'):
        print(f'{self.term.green}done {time() - start_time:.1f}s{self.term.normal}')

    def indented_event(self, text: str, indent: int = 0, end: str = '\n'):
        print(f'{self.term.normal}{" " * ((indent * 2) + 1)}↳ {text}{self.term.normal}', end=end)

    def output(self, output: str):
        wrapped_output = wrap_text_with_indentation(output, self.term.width)

        for line in wrapped_output.splitlines():
            sleep(0.02)
            print(line)

    def error(self, error: str, description: str):
        print(f' ↳ {self.term.red}Error: {self.term.normal}{error} !!!')
        self.red_divider()
        print(f'{description}')


