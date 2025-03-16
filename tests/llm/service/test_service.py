from unittest import TestCase

from dandy.llm.conf import llm_configs
from tests.llm.decorators import run_llm_configs


class TestService(TestCase):
    @run_llm_configs()
    def test_assistant_prompt(self, llm_config: str):
        str_response = llm_configs[llm_config].service.assistant_str_prompt_to_str('Hello, World!')

        self.assertTrue(str_response != '' and str_response is not None)

