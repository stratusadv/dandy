from unittest import TestCase

from dandy.agent.exceptions import AgentOverThoughtRecoverableException
from dandy.conf import settings
from dandy.core.processor.processor import BaseProcessor
from dandy.recorder import recorder_to_html_file
from tests.llm.agent.llm_agents import MuseumEmailLlmAgent

FROM_EMAIL_ADDRESS = 'a.person@some_place.com'

class TestLlmAgent(TestCase):
    def setUp(self) -> None:
        MuseumEmailLlmAgent.plan_time_limit_seconds = settings.DEFAULT_AGENT_PLAN_TIME_LIMIT_SECONDS
        MuseumEmailLlmAgent.plan_task_count_limit = settings.DEFAULT_AGENT_PLAN_TASK_COUNT_LIMIT

    def test_llm_agent_import(self):
        from dandy.agent import Agent

        self.assertTrue(type(Agent) is type(BaseProcessor))

    @recorder_to_html_file('test_llm_agent')
    def test_llm_agent_process(self):
        email = MuseumEmailLlmAgent.process(
            f'The Royal Tyrell Palaeontology Museum, green colors are awesome and my email is {FROM_EMAIL_ADDRESS}'
        )

        self.assertEqual(email.from_email_address, FROM_EMAIL_ADDRESS)

    def test_llm_agent_plan_time_limit(self):
        MuseumEmailLlmAgent.plan_time_limit_seconds = 1

        with self.assertRaises(AgentOverThoughtRecoverableException):
            MuseumEmailLlmAgent.process(
                f'The Royal Ontario Museum, I like the color blue and my email is {FROM_EMAIL_ADDRESS}'
            )

    def test_llm_agent_plan_task_count_limit(self):
        MuseumEmailLlmAgent.plan_task_count_limit = 1

        with self.assertRaises(AgentOverThoughtRecoverableException):
            MuseumEmailLlmAgent.process(
                f'The Canadian Museum of Nature with proof reading, my favorite color is purple and my email is {FROM_EMAIL_ADDRESS}'
            )



