# import os
# import sys
# import filecmp
# import shutil
# from io import StringIO
# from pathlib import Path
# from unittest import TestCase, mock
# from unittest.mock import MagicMock
#
# from dandy.cli.main import main
# from dandy.cli.utils import check_or_create_settings
# from dandy.conf import settings
# from dandy.constants import CLI_OUTPUT_DIRECTORY
# from dandy.intel.intel import BaseIntel
#
#
# class DefaultLlmIntel(BaseIntel):
#     text: str
#
#
# CLI_OUTPUT_PATH = Path(settings.BASE_PATH, CLI_OUTPUT_DIRECTORY)
# EVALUATE_MODULE_AND_OBJ = 'dandy.cli.llm.evaluate.intelligence.prompts.prompt_evaluation_prompts.evaluate_prompt_user_prompt'
# EVALUATE_DESCRIPTION = 'This prompt is used to evaluate the programmatic prompts used for interacting with large language models.'
# GENERATE_DESCRIPTION = 'An llm bot to generate a story about testing software.'
# ASSISTANT_DESCRIPTION = 'What is something fun you can do with the python coding language?'
#
#
# class TestCli(TestCase):
#     def setUp(self):
#         self.held = sys.stdout
#         sys.stdout = StringIO()
#
#     def tearDown(self):
#         sys.stdout = self.held
#
#     def test_cli_without_arguments(self):
#         test_args = []
#         with mock.patch('sys.argv', ['dandy'] + test_args):
#             main()
#
#         output = sys.stdout.getvalue().strip()
#
#         self.assertIn("usage: dandy [-h]", output)
#
#     def test_cli_calculate(self):
#         test_args = ['-c', '13', '16', '4096']
#         with mock.patch('sys.argv', ['dandy'] + test_args):
#             main()
#
#         output = sys.stdout.getvalue().strip()
#
#         self.assertIn("37.0096039", output)
#
#     def test_cli_evaluate_with_prompt_arg(self):
#         test_args = ['-e', 'prompt', '-p', EVALUATE_DESCRIPTION]
#         with (
#             mock.patch('sys.argv', ['dandy'] + test_args), \
#                 mock.patch('builtins.input', return_value=EVALUATE_MODULE_AND_OBJ)):
#             main()
#
#         self.assertTrue(True)
#
#     def test_cli_evaluate_without_prompt_arg(self):
#         test_args = ['-e', 'prompt']
#         with (
#             mock.patch('sys.argv', ['dandy'] + test_args), \
#                 mock.patch(
#                     'builtins.input',
#                     side_effect=[EVALUATE_MODULE_AND_OBJ, EVALUATE_DESCRIPTION])
#         ):
#             main()
#
#         self.assertTrue(True)
#
#     def _assert_generate_output_exists(self):
#         self.assertEqual(len(os.listdir(CLI_OUTPUT_PATH)), 1)
#
#         file_path = os.listdir(CLI_OUTPUT_PATH)[0]
#
#         with open(os.path.join(CLI_OUTPUT_PATH, file_path), 'r') as f:
#             self.assertNotEqual(f.read(), '')
#
#         shutil.rmtree(CLI_OUTPUT_PATH)
#
#     def test_cli_generate_with_prompt(self):
#         test_args = ['-g', 'llm_bot', '-p', GENERATE_DESCRIPTION]
#         with (
#             mock.patch('sys.argv', ['dandy'] + test_args), \
#                 ):
#             main()
#
#         self._assert_generate_output_exists()
#
#     def test_cli_generate_without_prompt(self):
#         test_args = ['-g', 'llm_bot']
#         with (
#             mock.patch('sys.argv', ['dandy'] + test_args), \
#                 mock.patch(
#                     'builtins.input', return_value=[GENERATE_DESCRIPTION])
#         ):
#             main()
#
#         self._assert_generate_output_exists()
#
#     def test_cli_assistant(self):
#         test_args = ['-a', 'prompt']
#
#         process_return = 'process was called, yay!'
#
#         with (
#             mock.patch('sys.argv', ['dandy'] + test_args), \
#                 mock.patch('builtins.input', return_value=ASSISTANT_DESCRIPTION), \
#                 mock.patch(
#                     'dandy.llm.LlmBot.process',
#                     return_value=DefaultLlmIntel(text=process_return)), \
#  \
#                 ):
#             main()
#
#         output = sys.stdout.getvalue().strip()
#         self.assertIn(process_return, output)
#
#     @mock.patch('importlib.import_module')
#     @mock.patch('dandy.cli.utils.get_settings_module_name')
#     def test_cli_check_or_create_settings_error(self, mock_get_settings_module_name: MagicMock,
#                                                 mock_import_module: MagicMock):
#         mock_import_module.side_effect = ImportError
#         mock_get_settings_module_name.return_value = 'new.test.settings'
#         test_cwd = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
#         test_settings_path = os.path.join(test_cwd, 'new', 'test', 'settings.py')
#
#         with self.assertRaises(SystemExit):
#             check_or_create_settings(test_cwd)
#
#         self.assertTrue(os.path.exists(test_settings_path))
#         self.assertTrue(filecmp.cmp(os.path.join(test_cwd, 'dandy', 'default_settings.py'), test_settings_path))
#
#         shutil.rmtree(os.path.join(test_cwd, 'new'))
