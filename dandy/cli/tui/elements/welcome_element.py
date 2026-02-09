from dandy import constants
from dandy.cli.conf import config
from dandy.cli.tui.elements.element import BaseElement
from dandy.llm.config import LlmConfig


class WelcomeElement(BaseElement):
    def render(self):
        print('')
        print('Dandy CLI Welcomes You !!!')
        print(self.term.bold_red('Version   : ') + constants.__VERSION__)
        print(self.term.bold_red('Model     : ') + LlmConfig('DEFAULT').model)
        print(self.term.bold_red('Directory : ') + str(config.project_base_path))
