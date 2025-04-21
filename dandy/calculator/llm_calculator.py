from dandy.calculator.calculations.llm.model_calculations import BitSizes, model_size_bytes_calculation, \
    model_memory_size_bytes_calculation, model_loading_size_bytes_calculation


def model_size_to_vram_gb(
        parameter_count_billions: float,
        quantization_size_bits: BitSizes
) -> float:
    parameter_count = parameter_count_billions * 1e9

    model_size_bytes = model_size_bytes_calculation(
        parameter_count,
    )

    model_landing_size_bytes = model_loading_size_bytes_calculation(
        quantization_size_bits,
    )

    model_memory_size_bytes = model_memory_size_bytes_calculation(
        model_size_bytes,
        model_landing_size_bytes
    )

    return model_memory_size_bytes / (1024 ** 3)


def model_and_token_size_to_vram_gb(
        parameter_count_billions: float,
        quantization_size_bits: BitSizes,
        token_count: int,
) -> float:
    parameter_count = parameter_count_billions * 1e9
    hidden_size = 768
    
    model_size_with_tokens = parameter_count + hidden_size * token_count
    
    return (model_size_with_tokens * (quantization_size_bits / 8)) / (1024 ** 3)
