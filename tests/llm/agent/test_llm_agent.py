from unittest import TestCase

from dandy.core.processor.processor import BaseProcessor
from dandy.recorder import recorder_to_html_file
from tests.llm.agent.llm_agents import MuseumEmailLlmAgent

FROM_EMAIL_ADDRESS = 'a.person@some_place.com'

class TestLlmAgent(TestCase):
    def test_llm_agent_import(self):
        from dandy.llm import BaseLlmAgent

        self.assertTrue(type(BaseLlmAgent) is type(BaseProcessor))

    @recorder_to_html_file('test_llm_agent')
    def test_llm_agent_process(self):
        email = MuseumEmailLlmAgent.process(
            f'The Royal Tyrell Palaeontology Museum, my email is {FROM_EMAIL_ADDRESS}'
        )

        self.assertEqual(email.from_email_address, FROM_EMAIL_ADDRESS)


