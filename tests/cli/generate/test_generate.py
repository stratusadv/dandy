# import os
# import shutil
# from unittest import TestCase, mock
#
# from dandy.cli.llm.generate.generate import generate, GenerateChoices
# from dandy.llm.conf import llm_configs
# from dandy.conf import settings
#
#
# class TestGenerate(TestCase):
#     def test_generate_llm_bot(self):
#         generate(
#             llm_config=llm_configs.DEFAULT,
#             choice=GenerateChoices.LLM_BOT,
#             generate_description='An llm bot to generate a story about testing software.',
#             output_path='',
#             output_to_file=False,
#         )
#
#         self.assertTrue(True)
#
#     @mock.patch('builtins.input')
#     def test_generate_llm_bot_no_description_output_to_file(self, input_mock: mock.MagicMock):
#         input_mock.return_value = 'An llm bot to generate a story about testing software.'
#
#         output_path = os.path.join(settings.BASE_PATH, '.dandy_generate_llm_bot_output')
#         if os.path.exists(output_path):
#             shutil.rmtree(output_path)
#
#         os.mkdir(output_path)
#
#         generate(
#             llm_config=llm_configs.DEFAULT,
#             choice=GenerateChoices.LLM_BOT,
#             generate_description=None,
#             output_path=output_path,
#             output_to_file=True,
#         )
#
#         # check if there is a file in output_path
#         self.assertEqual(len(os.listdir(output_path)), 1)
#
#         file_path = os.listdir(output_path)[0]
#
#         with open(os.path.join(output_path, file_path), 'r') as f:
#             self.assertNotEqual(f.read(), '')