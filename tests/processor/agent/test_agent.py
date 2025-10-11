from unittest import TestCase

from dandy.processor.agent.exceptions import AgentOverThoughtRecoverableException
from dandy.conf import settings
from dandy.processor.processor import BaseProcessor
from dandy.recorder import recorder_to_html_file
from tests.processor.agent.intelligence.agents import MuseumEmailAgent

FROM_EMAIL_ADDRESS = 'a.person@some_place.com'

class TestAgent(TestCase):
    def setUp(self) -> None:
        MuseumEmailAgent.plan_time_limit_seconds = settings.AGENT_DEFAULT_PLAN_TIME_LIMIT_SECONDS
        MuseumEmailAgent.plan_task_count_limit = settings.AGENT_DEFAULT_PLAN_TASK_COUNT_LIMIT

    def test_agent_import(self):
        from dandy.processor.agent.agent import Agent

        self.assertTrue(type(Agent) is type(BaseProcessor))

    @recorder_to_html_file('test_agent')
    def test_agent_process(self):
        email = MuseumEmailAgent().process(
            prompt=f'The Royal Tyrell Palaeontology Museum, green colors are awesome and the email I am sending from is {FROM_EMAIL_ADDRESS}'
        )

        self.assertEqual(email.from_email_address, FROM_EMAIL_ADDRESS)

    def test_agent_plan_time_limit(self):
        museum_email_agent = MuseumEmailAgent()
        museum_email_agent.plan_time_limit_seconds = 1

        with self.assertRaises(AgentOverThoughtRecoverableException):
            museum_email_agent.process(
                f'The Royal Ontario Museum, I like the color blue and my email is {FROM_EMAIL_ADDRESS}'
            )

    def test_agent_plan_task_count_limit(self):
        museum_email_agent = MuseumEmailAgent()
        museum_email_agent.plan_task_count_limit = 1

        with self.assertRaises(AgentOverThoughtRecoverableException):
            museum_email_agent.process(
                f'The Canadian Museum of Nature with proof reading, my favorite color is purple and my email is {FROM_EMAIL_ADDRESS}'
            )



