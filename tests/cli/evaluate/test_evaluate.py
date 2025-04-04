from unittest import TestCase

from dandy.cli.llm.evaluate.evaluate import evaluate, EvaluateChoices
from dandy.recorder.recorder import Recorder
from dandy.llm.conf import llm_configs


class TestEvaluate(TestCase):
    def test_evaluate_prompt(self):
        Recorder.start_recording('test_prompt_evaluation')

        evaluate(
            llm_config=llm_configs.DEFAULT,
            choice=EvaluateChoices.PROMPT,
            module_and_obj='dandy.cli.llm.evaluate.intelligence.prompts.prompt_evaluation_prompts.evaluate_prompt_system_prompt',
            evaluate_description='This prompt is used to evaluate the programmatic prompts used for interacting with large language models.'
        )

        Recorder.stop_recording('test_prompt_evaluation')
        Recorder.to_html_file('test_prompt_evaluation')

        self.assertTrue(True)
