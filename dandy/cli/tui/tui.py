import sys
import threading
import time

from blessed import Terminal

from dandy.cli.tui.elements.welcome_element import WelcomeElement


class Tui:
    term = Terminal()
    _timer_stop = False
    _action_commands = []

    @classmethod
    def clear(cls):
        print(cls.term.clear)

    @classmethod
    def _print_processing_timer(cls):
        start_time = time.time()
        hat_frames = ['🎩', '🪄', '✨', '🎩', '✨', '🪄']
        frame_index = 0

        while not cls._timer_stop:
            elapsed = time.time() - start_time
            current_hat = hat_frames[frame_index % len(hat_frames)]
            print(f'\r{cls.term.bold_green(" ↳ Processing ")} {current_hat} {cls.term.bold_white(f"{elapsed:.1f}s")}', end='',
                  flush=True)
            frame_index += 1
            time.sleep(0.15)

        print(cls.term.bold_green(' Done'))
        print(cls.term.bold_green('-' * cls.term.width))

    @classmethod
    def _get_matches(cls, text):
        """Get matching commands for autocomplete."""
        if not text.startswith('/'):
            return []

        text_without_slash = text[1:]
        matches = [f'/{cmd}' for cmd in cls._action_commands if cmd.startswith(text_without_slash)]
        return matches

    @classmethod
    def setup_autocomplete(cls, action_commands):
        """Setup autocomplete with action commands."""
        cls._action_commands = action_commands

    @classmethod
    def _display_autocomplete_hints(cls, matches, selected_index):
        """Display autocomplete options below the input line."""
        if not matches:
            return 0

        # Clear previous hints - use gray color instead of dim for Windows compatibility
        hint_text = cls.term.gray('  Options: ')
        for i, match in enumerate(matches):
            if i == selected_index:
                hint_text += cls.term.bold_cyan(f'{match} ')
            else:
                hint_text += cls.term.gray(f'{match} ')

        sys.stdout.write('\n' + hint_text)
        sys.stdout.flush()
        return 1  # Number of lines used for hints

    @classmethod
    def input(cls, sub_app: str | None = None, run_process_timer: bool = True):
        input_str = cls.term.bold_blue('🎩 ')

        if sub_app is not None:
            input_str += cls.term.bold_blue(sub_app) + ' > '

        print(cls.term.bold_blue('─' * cls.term.width))

        # Custom input with autocomplete support
        buffer = []
        match_index = 0
        current_matches = []
        hint_lines = 0

        with cls.term.cbreak():
            sys.stdout.write(input_str)
            sys.stdout.flush()

            while True:
                key = cls.term.inkey(timeout=None)

                if key.name == 'KEY_ENTER' or key == '\n' or key == '\r':
                    # Clear hint lines before accepting input
                    if hint_lines > 0:
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_down(1))
                        sys.stdout.write('\r' + cls.term.clear_eol())
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_up(1))
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    break
                elif key.name == 'KEY_BACKSPACE' or key == '\x7f' or key == '\x08':
                    if buffer:
                        buffer.pop()
                        # Clear hint lines
                        if hint_lines > 0:
                            for _ in range(hint_lines):
                                sys.stdout.write(cls.term.move_down(1))
                            sys.stdout.write('\r' + cls.term.clear_eol())
                            for _ in range(hint_lines):
                                sys.stdout.write(cls.term.move_up(1))
                        hint_lines = 0
                        # Redraw line
                        sys.stdout.write('\r' + cls.term.clear_eol())
                        sys.stdout.write(input_str + ''.join(buffer))

                        # Check for new matches after backspace
                        current_text = ''.join(buffer)
                        if current_text.startswith('/') and len(current_text) > 1:
                            current_matches = cls._get_matches(current_text)
                            match_index = 0
                            # Display hints
                            if current_matches:
                                hint_lines = cls._display_autocomplete_hints(current_matches, -1)
                                # Move cursor back to input line
                                for _ in range(hint_lines):
                                    sys.stdout.write(cls.term.move_up(1))
                                sys.stdout.write('\r' + input_str + ''.join(buffer))
                        else:
                            current_matches = []
                            match_index = 0

                        sys.stdout.flush()
                elif key.name == 'KEY_TAB' or key == '\t':
                    # Tab pressed - autocomplete
                    current_text = ''.join(buffer)
                    if not current_matches or current_text != getattr(cls, '_last_autocomplete_text', ''):
                        current_matches = cls._get_matches(current_text)
                        match_index = 0
                        cls._last_autocomplete_text = current_text

                    if current_matches:
                        # Cycle through matches
                        buffer = list(current_matches[match_index % len(current_matches)])

                        # Clear hint lines
                        if hint_lines > 0:
                            for _ in range(hint_lines):
                                sys.stdout.write(cls.term.move_down(1))
                            sys.stdout.write('\r' + cls.term.clear_eol())
                            for _ in range(hint_lines):
                                sys.stdout.write(cls.term.move_up(1))

                        # Redraw line
                        sys.stdout.write('\r' + cls.term.clear_eol())
                        sys.stdout.write(input_str + ''.join(buffer))

                        # Display hints
                        hint_lines = cls._display_autocomplete_hints(current_matches, match_index % len(current_matches))

                        # Move cursor back to input line
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_up(1))
                        sys.stdout.write('\r' + input_str + ''.join(buffer))
                        sys.stdout.flush()

                        match_index += 1
                elif key.is_sequence:
                    # Ignore other special keys
                    pass
                else:
                    # Regular character
                    buffer.append(key)
                    current_text = ''.join(buffer)

                    # Clear old hints
                    if hint_lines > 0:
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_down(1))
                        sys.stdout.write('\r' + cls.term.clear_eol())
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_up(1))

                    # Check for new matches
                    if current_text.startswith('/') and len(current_text) > 1:
                        current_matches = cls._get_matches(current_text)
                        match_index = 0

                        # Display new hints
                        sys.stdout.write(key)
                        hint_lines = cls._display_autocomplete_hints(current_matches, -1)

                        # Move cursor back to input line
                        for _ in range(hint_lines):
                            sys.stdout.write(cls.term.move_up(1))
                        sys.stdout.write('\r' + input_str + ''.join(buffer))
                    else:
                        current_matches = []
                        match_index = 0
                        hint_lines = 0
                        sys.stdout.write(key)

                    sys.stdout.flush()

        user_input = ''.join(buffer)
        if user_input == '':
            return None

        if run_process_timer:
            cls._timer_stop = False
            timer_thread = threading.Thread(target=cls._print_processing_timer, daemon=True)
            timer_thread.start()
        else:
            cls._timer_stop = True

        def stop_timer():
            if cls._timer_stop:
                return

            cls._timer_stop = True
            timer_thread.join(timeout=0.5)

        return user_input, stop_timer

    @classmethod
    def print(cls, content: str):
        print(content)


    @classmethod
    def print_welcome(cls):
        WelcomeElement(cls.term).render()
