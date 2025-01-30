from unittest import TestCase

from dandy.processor.processor import BaseProcessor


class TestWorkflow(TestCase):
    def test_workflow_import(self):
        from dandy.workflow import Workflow
        self.assertTrue(type(Workflow) is type(BaseProcessor))