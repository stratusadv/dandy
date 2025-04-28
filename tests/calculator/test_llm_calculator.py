from unittest import TestCase

from dandy.calculator import llm_calculator

PARAMETER_COUNT_BILLIONS = 13
QUANTIZATION_SIZE_BITS = 16
TOKEN_COUNT = 4096


class TestLlmCalculator(TestCase):
    def test_model_size_to_vram_gb(self):
        self.assertEqual(
            llm_calculator.model_size_for_inference_to_vram_gb(
                PARAMETER_COUNT_BILLIONS,
                QUANTIZATION_SIZE_BITS,
            ),
            29.05726432800293
        )
        
    def test_model_and_token_size_to_vram_gb(self):
        self.assertEqual(
            llm_calculator.model_size_and_token_count_for_inference_to_vram_gb(
                PARAMETER_COUNT_BILLIONS,
                QUANTIZATION_SIZE_BITS,
                TOKEN_COUNT,
            ),
            37.00960397720337
        )

