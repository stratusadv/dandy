from unittest import TestCase

from dandy.infrastructure import recorder
from dandy.shared.exceptions import DandyRecoverableError
from dandy.infrastructure.recorder.decorators import recorder_to_html_file
from tests.domain.intel.intelligence.bots import JsonSchemaBot
from tests.domain.intel.intelligence.intel import OfficeIntel, PersonIntel
from tests.shared.decorators import run_llm_configs


class TestJsonSchemaWithLlm(TestCase):
    @recorder_to_html_file('test_json_schema_with_llm')
    @run_llm_configs()
    def test_json_schema_with_gt_lt_field(self, llm_config: str):
        json_schema_bot = JsonSchemaBot(
            llm_config=llm_config
        )

        try:
            _ = json_schema_bot.llm.prompt_to_intel(
                prompt='Describe my dream office',
                intel_class=OfficeIntel
            )

            self.assertTrue(True)
        except DandyRecoverableError:
            self.assertTrue(False)



    @run_llm_configs()
    def test_json_schema_with_complex_intel(self, llm_config: str):
        json_schema_bot = JsonSchemaBot(
            llm_config=llm_config
        )

        try:
            _ = json_schema_bot.llm.prompt_to_intel(
                prompt='Describe a interesting person I may meet in the future.',
                intel_class=PersonIntel
            )

            self.assertTrue(True)
        except DandyRecoverableError:
            self.assertTrue(False)


