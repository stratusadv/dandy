import os
from unittest import TestCase

from dandy import config
from dandy.job.job import Job

from tests.prompts import business_idea_input_prompt
from tests.models import BusinessIdeaEvaluationSchema
from tests.workflows import BusinessIdeaEvaluationWorkflow

config.setup_ollama(
    url=os.getenv("OLLAMA_URL"),
    port=int(os.getenv("OLLAMA_PORT"))
)

client_idea_job = Job(
    input_prompt=business_idea_input_prompt(),
    output_schema=BusinessIdeaEvaluationSchema,
    workflow=BusinessIdeaEvaluationWorkflow,
)

client_idea_job.process()
