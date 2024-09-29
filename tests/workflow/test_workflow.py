from unittest import TestCase

from dandy.handler.handler import Handler


class TestWorkflow(TestCase):
    def test_workflow_import(self):
        from dandy.workflow import Workflow
        self.assertTrue(type(Workflow) is type(Handler))