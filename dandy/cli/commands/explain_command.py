from dandy import Bot, Prompt
from dandy.cli.commands.command import BaseCommand
from dandy.conf import settings


class ExplainCommand(BaseCommand):
    name = 'Explain'
    description = 'This will explain what the current project does.'
    calls = ('e', 'explain')

    def help(self):
        print('Chat help')

    def run(self):
        directory_list_prompt = (
            Prompt()
            .text('Explain to me what this current project is doing?')
            .text('Please provide a general overview paragraph and a list of functionality.')
            .text('At the end make a list of the 5 best files to explore to learn more about the project.')
            .sub_heading('Project Structure:')
            .directory_list(settings.BASE_PATH, max_depth=3)
        )
        response = Bot().process(directory_list_prompt)
        print(response.text)
