from dandy import consts
from dandy.cli.conf import config
from dandy.cli.tui.elements.element import BaseElement
from dandy.llm.conf import LlmConfigs


class WelcomeElement(BaseElement):
    def render(self):
        print('')
        print('Dandy CLI Welcomes You !!!')
        print(self.term.bold_red('Version   : ') + consts.__VERSION__)
        print(self.term.bold_red('Model     : ') + LlmConfigs().DEFAULT.model)
        print(self.term.bold_red('Directory : ') + str(config.project_base_path))
