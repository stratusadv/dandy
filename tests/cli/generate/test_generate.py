from unittest import TestCase

from dandy.cli.llm.generate.generate import generate, GenerateChoices
from dandy.llm.conf import llm_configs


class TestGenerate(TestCase):
    def test_generate_llm_bot(self):
        generate(
            llm_config=llm_configs.DEFAULT,
            choice=GenerateChoices.LLM_BOT,
            generate_description='An llm bot to generate a story about testing software.',
            output_path='',
            output_to_file=False,
        )

        self.assertTrue(True)
