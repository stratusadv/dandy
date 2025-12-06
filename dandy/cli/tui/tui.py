from typing import Sequence

from blessed import Terminal


class Tui:
    term = Terminal()

    @classmethod
    def clear(cls):
        print(cls.term.clear)

    @classmethod
    def input(cls, sub_apps: Sequence[str] | None = None):
        return input(cls.term.bold_blue('Dandy ') + cls.term.bold_white('> '))

    def print(self):
        pass

