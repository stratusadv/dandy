from unittest import TestCase

from dandy.job.job import Job
from tests.schemas import BusinessIdeaEvaluationSchema
from tests.workflows import BusinessIdeaEvaluationWorkflow


class TestDandy(TestCase):
    def setUp(self):
        self.client_input = 'hotdog stand'
        self.client_idea_job = Job(
            input=self.client_input,
            output_schema=BusinessIdeaEvaluationSchema,
            workflow=BusinessIdeaEvaluationWorkflow,
        )

    def test_job(self):
        pass