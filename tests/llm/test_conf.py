
from unittest import TestCase, mock

from dandy.core.exceptions import DandyException
from dandy.llm.conf import LlmConfigs
from dandy.conf import settings, DandySettings


class TestLlmConfigs(TestCase):
    def test_llm_config_raises_if_llm_configs_not_dict(self):
        with mock.patch.object(DandySettings, '__getattr__', return_value='not a dict'):
            with self.assertRaises(DandyException):
                LlmConfigs()

    def test_llm_config_raises_if_llm_configs_is_none(self):
        with mock.patch.object(DandySettings, '__getattr__', return_value=None):
            with self.assertRaises(DandyException):
                LlmConfigs()

    def test_llm_config_raises_if_llm_configs_is_missing_default(self):
        with mock.patch.object(DandySettings, '__getattr__', return_value={'NON_DEFAULT': {}}):
            with self.assertRaises(DandyException):
                LlmConfigs()

    def test_llm_config_raises_when_invalid_config_accessed(self):
        llm_configs = LlmConfigs()
        with self.assertRaises(DandyException):
            invalid_config = llm_configs.INVALID