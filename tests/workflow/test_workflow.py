from unittest import TestCase

from dandy.processor import BaseProcessor


class TestWorkflow(TestCase):
    def test_workflow_import(self):
        from dandy.workflow import BaseWorkflow
        self.assertTrue(type(BaseWorkflow) is type(BaseProcessor))