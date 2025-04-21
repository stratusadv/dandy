from typing_extensions import Literal

BitSizes = Literal[64, 32, 16, 8, 6, 5, 4, 3, 2]


def model_size_bytes_calculation(
        parameter_count: int | float,
        quantization_size_bits: BitSizes
) -> int:
    return int(parameter_count * (quantization_size_bits / 8))


def model_loading_size_bytes_calculation(
        parameter_size_bits: BitSizes
) -> float:
    return float(32 / parameter_size_bits)


def model_memory_size_bytes_calculation(
        model_size_bytes: int,
        model_loading_size_bytes: float,
) -> float:
    return model_size_bytes / model_loading_size_bytes