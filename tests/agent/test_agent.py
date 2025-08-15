from unittest import TestCase

from dandy.core.processor import BaseProcessor


class TestAgent(TestCase):
    def test_agent_import(self):
        from dandy.agent import BaseAgent
        self.assertTrue(type(BaseAgent) is type(BaseProcessor))
