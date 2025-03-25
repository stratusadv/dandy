from unittest import TestCase

from dandy.core.exceptions import DandyRecoverableException
from dandy.debug.decorators import debug_recorder_to_html
from tests.llm.decorators import run_llm_configs
from tests.llm.json.intel import OfficeIntel
from tests.llm.json.llm_bots import JsonSchemaLlmBot


class TestJsonSchemaWithLlm(TestCase):
    @debug_recorder_to_html('test_json_schema_with_gt_lt_field')
    @run_llm_configs()
    def test_json_schema_with_gt_lt_field(self, llm_config: str):
        JsonSchemaLlmBot.config = llm_config

        try:
            _ = JsonSchemaLlmBot.process(
                prompt='Describe my dream office',
                intel_class=OfficeIntel
            )

            self.assertTrue(True)
        except DandyRecoverableException:
            self.assertTrue(False)


