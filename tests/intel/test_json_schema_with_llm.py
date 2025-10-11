from unittest import TestCase

from dandy.core.exceptions import DandyRecoverableException
from tests.llm.decorators import run_llm_configs
from tests.intel.intelligence.intel import OfficeIntel
from tests.intel.intelligence.bots import JsonSchemaBot


class TestJsonSchemaWithLlm(TestCase):
    @run_llm_configs()
    def test_json_schema_with_gt_lt_field(self, llm_config: str):
        JsonSchemaBot().llm_config = llm_config

        try:
            _ = JsonSchemaBot().llm.prompt_to_intel(
                prompt='Describe my dream office',
                intel_class=OfficeIntel
            )

            self.assertTrue(True)
        except DandyRecoverableException:
            self.assertTrue(False)


