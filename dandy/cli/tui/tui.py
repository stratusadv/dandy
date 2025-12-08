
from blessed import Terminal
from dandy import consts
from dandy.conf import settings
from dandy.llm.conf import llm_configs


class Tui:
    term = Terminal()

    @classmethod
    def clear(cls):
        print(cls.term.clear)

    @classmethod
    def input(cls, sub_app: str | None = None):
        input_str = cls.term.bold_blue('>>> ')

        if sub_app is not None:
            input_str += cls.term.bold_blue(sub_app) + ' > '

        user_input = input(input_str)

        if user_input == '':
            return None

        cls.print(cls.term.bold_green('Processing ') + cls.term.bold_white('...'))

        return user_input

    @classmethod
    def print(cls, content: str):
        print(content)


    @classmethod
    def print_welcome(cls):
        cls.print('')
        cls.print('Dandy CLI Welcomes You !!!')
        cls.print(cls.term.bold_red('Version   : ') + consts.__VERSION__)
        cls.print(cls.term.bold_red('Model     : ') + llm_configs.DEFAULT.model)
        cls.print(cls.term.bold_red('Directory : ') + str(settings.BASE_PATH))
