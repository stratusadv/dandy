from unittest import TestCase, mock

from dandy.cli.llm.assistant.assistant import assistant
from dandy.llm.conf import llm_configs


ASSISTANT_DESCRIPTION = 'What is something fun you can do with the python coding language?'


class TestAssistant(TestCase):
    def test_assistant(self):
        assistant(
            llm_config='DEFAULT',
            user_prompt=ASSISTANT_DESCRIPTION
        )

        self.assertTrue(True)

    def test_assistant_without_prompt(self):
        with mock.patch('builtins.input', return_value=ASSISTANT_DESCRIPTION):
            assistant(
                llm_config='DEFAULT',
                user_prompt=''
            )

            self.assertTrue(True)
