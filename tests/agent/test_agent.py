from unittest import TestCase

from dandy.processor.processor import BaseProcessor


class TestAgent(TestCase):
    def test_agent_import(self):
        from dandy.processor.agent.agent import Agent
        self.assertTrue(type(Agent) is type(BaseProcessor))
