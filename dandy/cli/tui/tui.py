import random
import sys
from time import time

from blessed import Terminal

from dandy import constants
from dandy.cli.actions.action import BaseAction
from dandy.cli.conf import config
from dandy.cli.constants import PROCESSING_PHRASES
from dandy.cli.tui.tools import wrap_text_with_indentation
from dandy.llm.config import LlmConfig


class Tui:
    term = Terminal()
    _action_commands = []

    @classmethod
    def clear(cls):
        print(cls.term.clear)

    @classmethod
    def _get_matching_actions(cls, text: str) -> list[str]:
        if not text.startswith('/'):
            return []

        text_without_slash = text[1:]
        matches = [
            f'/{cmd}'
            for cmd in cls._action_commands
            if cmd.startswith(text_without_slash)
        ]
        return matches

    @classmethod
    def setup_autocomplete(cls, action_commands: list):
        """Setup autocomplete with action commands."""
        cls._action_commands = action_commands

    @classmethod
    def _display_autocomplete_hints(cls, action_matches: list, selected_index: int) -> int:
        """Display autocomplete options below the input line."""
        if not action_matches:
            return 0

        # Clear previous hints - use gray color instead of dim for Windows compatibility
        hint_text = cls.term.gray('  Options: ')
        for i, match in enumerate(action_matches):
            if i == selected_index:
                hint_text += cls.term.bold_cyan(f'{match} ')
            else:
                hint_text += cls.term.gray(f'{match} ')

        sys.stdout.write('\n' + hint_text)
        sys.stdout.flush()

        return 1  # Number of lines used for hints

    @classmethod
    def _clear_hint_lines(cls, hint_lines: int):
        if hint_lines > 0:
            for _ in range(hint_lines):
                sys.stdout.write(cls.term.move_down(1))
            sys.stdout.write('\r' + cls.term.clear_eol())
            for _ in range(hint_lines):
                sys.stdout.write(cls.term.move_up(1))

    @classmethod
    def get_user_input(cls, run_process_timer: bool = True):
        print(cls.term.bold_blue('─' * cls.term.width))
        input_prefix = cls.term.bold_blue('🎩 ')

        # Custom input with autocomplete support
        buffer = []
        match_index = 0
        current_matches = []
        hint_lines = 0

        with cls.term.cbreak():
            sys.stdout.write(input_prefix)
            sys.stdout.flush()

            while True:
                key = cls.term.inkey(timeout=None)

                if key.name == 'KEY_ENTER' or key in {'\n', '\r'}:
                    if buffer:
                        cls._clear_hint_lines(hint_lines)
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                        break

                elif key.name == 'KEY_BACKSPACE' or key in {'\x7f', '\x08'}:
                    if buffer:
                        buffer.pop()
                        cls._clear_hint_lines(hint_lines)
                        hint_lines = 0
                        # Redraw line
                        sys.stdout.write('\r' + cls.term.clear_eol())
                        sys.stdout.write(input_prefix + ''.join(buffer))

                        # Check for new matches after backspace
                        current_text = ''.join(buffer)
                        if current_text.startswith('/') and len(current_text) > 1:
                            current_matches = cls._get_matching_actions(current_text)
                            match_index = 0
                            # Display hints
                            if current_matches:
                                hint_lines = cls._display_autocomplete_hints(
                                    current_matches, -1
                                )
                                # Move cursor back to input line
                                for _ in range(hint_lines):
                                    sys.stdout.write(cls.term.move_up(1))

                                sys.stdout.write('\r' + input_prefix + ''.join(buffer))
                        else:
                            current_matches = []
                            match_index = 0

                        sys.stdout.flush()
                elif key.name == 'KEY_TAB' or key == '\t':
                    # Tab pressed - autocomplete
                    current_text = ''.join(buffer)
                    if not current_matches or current_text != getattr(
                        cls, '_last_autocomplete_text', ''
                    ):
                        current_matches = cls._get_matching_actions(current_text)
                        match_index = 0
                        cls._last_autocomplete_text = current_text

                    if current_matches:
                        # Cycle through matches
                        buffer = list(
                            current_matches[match_index % len(current_matches)]
                        )

                        cls._clear_hint_lines(hint_lines)

                        # Redraw line
                        sys.stdout.write('\r' + cls.term.clear_eol())
                        sys.stdout.write(input_prefix + ''.join(buffer))

                        # Display hints
                        hint_lines = cls._display_autocomplete_hints(
                            current_matches, match_index % len(current_matches)
                        )

                        # Move cursor back to input line
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_up(1))
                        sys.stdout.write('\r' + input_prefix + ''.join(buffer))
                        sys.stdout.flush()

                        match_index += 1
                elif key.is_sequence:
                    # Ignore other special keys
                    pass
                else:
                    # Regular character
                    buffer.append(key)
                    current_text = ''.join(buffer)

                    cls._clear_hint_lines(hint_lines)

                    # Check for new matches
                    if current_text.startswith('/') and len(current_text) > 1:
                        current_matches = cls._get_matching_actions(current_text)
                        match_index = 0

                        # Display new hints
                        sys.stdout.write(key)
                        hint_lines = cls._display_autocomplete_hints(
                            current_matches, -1
                        )

                        # Move cursor back to input line
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_up(1))
                        sys.stdout.write('\r' + input_prefix + ''.join(buffer))
                    else:
                        current_matches = []
                        match_index = 0
                        hint_lines = 0
                        sys.stdout.write(key)

                    sys.stdout.flush()

        return ''.join(buffer)

    @classmethod
    def print(cls, content: str):
        print(content)


    @classmethod
    def print_welcome(cls):
        print('')
        print('Dandy CLI Welcomes You !!!')
        print(cls.term.bold_purple('─' * cls.term.width))
        print(cls.term.bold_purple('Version   : ') + constants.__VERSION__)
        print(cls.term.bold_purple('Model     : ') + LlmConfig('DEFAULT').model)
        print(cls.term.bold_purple('Directory : ') + str(config.project_base_path))

    @classmethod
    def print_running_action(cls, action: BaseAction):
        phrase = random.choice(PROCESSING_PHRASES)
        print(f' ↳ {cls.term.bold_blue}{phrase} in preparation of "{action.name_gerund}" {cls.term.normal}',)

    @classmethod
    def print_completed_action(cls, start_time: float, action: BaseAction):
        print(f'   ↳ {cls.term.bold_green}Finished in only {time() - start_time:.1f}s{cls.term.normal}',)

    @classmethod
    def print_start_task(cls, action_name: str, task: str) -> float:
        print(f'   ↳ {cls.term.bold_orange}{action_name}{cls.term.normal} "{task}" ... ', end='')
        return time()

    @classmethod
    def print_end_task(cls, start_time: float, action_name: str = 'done'):
        print(f'{cls.term.green}done {time() - start_time:.1f}s{cls.term.normal}')

    @classmethod
    def print_output(cls, output: str):
        print(cls.term.bold_green('─' * cls.term.width), flush=True)
        print(wrap_text_with_indentation(output, cls.term.width))


