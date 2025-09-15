# from unittest import TestCase, mock
#
# from dandy.cli.llm.evaluate.evaluate import evaluate, EvaluateChoices
# from dandy.recorder.recorder import Recorder
# from dandy.llm.conf import llm_configs
#
#
# EVALUATE_MODULE_AND_OBJ = 'dandy.cli.llm.evaluate.intelligence.prompts.prompt_evaluation_prompts.evaluate_prompt_user_prompt'
# EVALUATE_DESCRIPTION = 'This prompt is used to evaluate the programmatic prompts used for interacting with large language models.'
#
#
# class TestEvaluate(TestCase):
#     def test_evaluate_prompt(self):
#         Recorder.start_recording('test_prompt_evaluation')
#
#         evaluate(
#             llm_config=llm_configs.DEFAULT,
#             choice=EvaluateChoices.PROMPT,
#             module_and_obj=EVALUATE_MODULE_AND_OBJ,
#             evaluate_description=EVALUATE_DESCRIPTION
#         )
#
#         Recorder.stop_recording('test_prompt_evaluation')
#         Recorder.to_html_file('test_prompt_evaluation')
#
#         self.assertTrue(True)