from unittest import TestCase

from dandy.cli.llm.evaluate.evaluate import evaluate, EvaluateChoices
from dandy.llm.conf import llm_configs


class TestEvaluate(TestCase):
    def test_evaluate_prompt(self):
        evaluate(
            llm_config=llm_configs.DEFAULT,
            choice=EvaluateChoices.PROMPT,
            module_and_obj='dandy.cli.evaluate.intelligence.prompts.prompt_evaluation_prompts.evaluate_prompt_system_prompt',
            evaluate_description='This prompt is used to evaluate the programmatic prompts used for interacting with large language models'
        )

        self.assertTrue(True)
