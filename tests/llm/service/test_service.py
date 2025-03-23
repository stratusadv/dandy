from unittest import TestCase

from dandy.llm.conf import llm_configs
from dandy.llm.intel import DefaultLlmIntel
from tests.llm.decorators import run_llm_configs


class TestService(TestCase):
    @run_llm_configs()
    def test_process_prompt_to_intel(self, llm_config: str):
        response = llm_configs[llm_config].service.process_prompt_to_intel(
            prompt='Hello, World!',
            intel_class=DefaultLlmIntel,
        )

        self.assertTrue(response.text != '' and response.text is not None)

