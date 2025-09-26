import importlib
from unittest import TestCase, mock

from dandy import default_settings
from dandy.conf import settings, DandySettings
from dandy.core.exceptions import DandyCriticalException
from dandy.core.utils import get_settings_module_name


class TestSettings(TestCase):
    def test_settings(self):
        self.assertEqual(
            default_settings.LLM_DEFAULT_PROMPT_RETRY_COUNT,
            settings.LLM_DEFAULT_PROMPT_RETRY_COUNT
        )

    @mock.patch('importlib.import_module')
    def test_dandy_settings_raises_dandy_critical_exception_with_invalid_module(self, mock_import_module: mock.MagicMock):
        mock_import_module.side_effect = ImportError
        with self.assertRaises(DandyCriticalException):
            DandySettings()

    @mock.patch('dandy.toolbox.utils.get_settings_module_name')
    def test_dandy_settings_defaults_to_tests_dandy_settings_if_missing_user_settings(
            self,
            mock_get_settings_module_name: mock.MagicMock
    ):
        mock_get_settings_module_name.return_value = None

        dandy_settings = DandySettings()
        dandy_settings_module_in_tests = importlib.import_module('tests.dandy_settings')

        self.assertEqual(dandy_settings._user_settings, dandy_settings_module_in_tests)

    def test_dandy_settings_raises_dandy_critical_exception_with_none_BASE_PATH(self):
        from dandy import default_settings
        original_default_base_path = default_settings.BASE_PATH
        default_settings.BASE_PATH = None

        settings_module = importlib.import_module(get_settings_module_name())
        original_settings_base_path = settings_module.BASE_PATH
        settings_module.BASE_PATH = None

        with self.assertRaises(DandyCriticalException):
            DandySettings()

        default_settings.BASE_PATH = original_default_base_path
        settings_module.BASE_PATH = original_settings_base_path


    def test_dandy_settings_raises_dandy_critical_exception_with_none_LLM_CONFIGS(self):
        from dandy import default_settings
        original_default_llm_configs = default_settings.LLM_CONFIGS
        default_settings.LLM_CONFIGS = None

        settings_module = importlib.import_module(get_settings_module_name())
        original_settings_llm_configs = settings_module.LLM_CONFIGS
        settings_module.LLM_CONFIGS = None

        with self.assertRaises(DandyCriticalException):
            DandySettings()

        default_settings.LLM_CONFIGS = original_default_llm_configs
        settings_module.LLM_CONFIGS = original_settings_llm_configs