from typing import Literal, TypeVar

from dandy.calculator.calculations.calculations import bits_to_bytes

BitSizes = Literal[64, 32, 16, 8, 6, 5, 4, 3, 2]

QuantizationBitSizes = TypeVar("QuantizationBitSizes", bound=BitSizes)

def hidden_dimension_and_number_of_layers_from_parameter_count(
        parameter_count: float,
) -> tuple[int, int]:
    parameter_count_billions = parameter_count / 1e9

    hidden_dimension = (
        (671, 20480, 160),
        (405, 16384, 120),
        (120, 12288, 96),
        (65, 8192, 80),
        (30, 7168, 60),
        (13, 5120, 40),
        (7, 4096, 32),
        (3, 3072, 26),
        (1, 2048, 22),
        (0, 1024, 18),
    )

    for value in hidden_dimension:
        if parameter_count_billions >= value[0]:
            return value[1], value[2]

    message = 'Invalid parameter count'
    raise ValueError(message)


def key_value_cache_per_token_size_bytes_calculation(
        hidden_dimension: int,
        quantization_size_bits: int,
        number_of_layers: int,
) -> float:
    return hidden_dimension * 2 * bits_to_bytes(quantization_size_bits) * number_of_layers


def key_value_cache_size_bytes_calculation(
        batch_size: int,
        sequence_length: int,
        key_value_cache_per_token_size_bytes: float,
) -> float:
    return batch_size * sequence_length * key_value_cache_per_token_size_bytes


def model_inference_activation_size_bytes_calculation(
        model_size_bytes: float,
) -> float:
    return model_size_bytes * 0.2


def model_size_bytes_calculation(
        parameter_count: float,
        quantization_size_bits: QuantizationBitSizes
) -> int | float:
    return parameter_count * bits_to_bytes(quantization_size_bits)


def model_training_activation_size_bytes_calculation(
        model_size_bytes: float,
) -> float:
    return model_size_bytes * 2.0


