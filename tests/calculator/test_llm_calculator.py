from unittest import TestCase

from dandy.calculator import llm_calculator


class TestLlmCalculator(TestCase):
    def test_model_size_to_vram_gb(self):
        self.assertEqual(
            llm_calculator.model_size_to_vram_gb(
                70,
                4,
            ),
            32.59629011154175
        )
        
    def test_model_and_token_size_to_vram_gb(self):
        self.assertEqual(
            llm_calculator.model_and_token_size_to_vram_gb(
                70,
                4,
                128000,
            ),
            32.59629011154175
        )

