import threading
import time

from blessed import Terminal

from dandy.cli.tui.elements.welcome_element import WelcomeElement


class Tui:
    term = Terminal()
    _timer_stop = False

    @classmethod
    def clear(cls):
        print(cls.term.clear)

    @classmethod
    def _print_processing_timer(cls):
        start_time = time.time()

        while not cls._timer_stop:
            elapsed = time.time() - start_time
            print(f'\r{cls.term.bold_green(" ↳ Processing ")} {cls.term.bold_white(f"{elapsed:.1f}s")}', end='',
                  flush=True)
            time.sleep(0.1)

        print(cls.term.bold_green(' Done'))
        print(cls.term.bold_green('-' * cls.term.width))

    @classmethod
    def input(cls, sub_app: str | None = None, run_process_timer: bool = True):
        input_str = cls.term.bold_blue('🎩 ')

        if sub_app is not None:
            input_str += cls.term.bold_blue(sub_app) + ' > '

        print(cls.term.bold_blue('─' * cls.term.width))
        user_input = input(input_str)
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
