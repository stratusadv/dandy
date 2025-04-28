from unittest import TestCase

from dandy.calculator.calculations.llm import model_calculations


PARAMETER_COUNT = 13_000_000_000
QUANTIZATION_SIZE_BITS = 16
HIDDEN_DIMENSION = 5_120
NUMBER_OF_LAYERS = 40
KEY_VALUE_CACHE_PER_TOKEN_SIZE_BYTES = 819_200
KEY_VALUE_CACHE_SIZE_BYTES = 3_355_443_200
MODEL_SIZE_BYTES = 26_000_000_000
MODEL_INFERENCE_ACTIVATION_SIZE_BYTES = 5_200_000_000
MODEL_TRAINING_ACTIVATION_SIZE_BYTES = 52_000_000_000
BATCH_SIZE = 1
SEQUENCE_LENGTH = 4_096



class TestModelCalculations(TestCase):
    def test_hidden_dimension_and_number_of_layers_from_parameter_count(self):
        self.assertEqual(
            model_calculations.hidden_dimension_and_number_of_layers_from_parameter_count(
                PARAMETER_COUNT,
            ),
            (HIDDEN_DIMENSION, NUMBER_OF_LAYERS)
        )

    def test_key_value_cache_per_token_size_bytes_calculation(self):
        self.assertEqual(
            model_calculations.key_value_cache_per_token_size_bytes_calculation(
                HIDDEN_DIMENSION,
                QUANTIZATION_SIZE_BITS,
                NUMBER_OF_LAYERS,
            ),
            KEY_VALUE_CACHE_PER_TOKEN_SIZE_BYTES
        )

    def test_key_value_cache_size_bytes_calculation(self):
        self.assertEqual(
            model_calculations.key_value_cache_size_bytes_calculation(
                BATCH_SIZE,
                SEQUENCE_LENGTH,
                KEY_VALUE_CACHE_PER_TOKEN_SIZE_BYTES,
            ),
            KEY_VALUE_CACHE_SIZE_BYTES
        )

    def test_model_inference_activation_size_bytes_calculation(self):
        self.assertEqual(
            model_calculations.model_inference_activation_size_bytes_calculation(
                MODEL_SIZE_BYTES,
            ),
            MODEL_INFERENCE_ACTIVATION_SIZE_BYTES
        )

    def test_model_size_bytes_calculation(self):
        self.assertEqual(
            model_calculations.model_size_bytes_calculation(
                PARAMETER_COUNT,
                QUANTIZATION_SIZE_BITS,
            ),
            MODEL_SIZE_BYTES
        )

    def test_model_training_activation_size_bytes_calculation(self):
        self.assertEqual(
            model_calculations.model_training_activation_size_bytes_calculation(
                MODEL_SIZE_BYTES,
            ),
            MODEL_TRAINING_ACTIVATION_SIZE_BYTES
        )

