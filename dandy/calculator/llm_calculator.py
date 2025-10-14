from dandy.calculator.calculations.llm import model_calculations


def model_size_for_inference_to_vram_gb(
        parameter_count_billions: float,
        quantization_size_bits: model_calculations.QuantizationBitSizes
) -> float:
    parameter_count = parameter_count_billions * 1e9

    model_size_bytes = model_calculations.model_size_bytes_calculation(
        parameter_count,
        quantization_size_bits
    )

    model_inference_activation_size_bytes = model_calculations.model_inference_activation_size_bytes_calculation(
        model_size_bytes
    )

    model_memory_size_bytes = model_size_bytes + model_inference_activation_size_bytes

    return model_memory_size_bytes / (1024 ** 3)


def model_size_and_token_count_for_inference_to_vram_gb(
        parameter_count_billions: float,
        quantization_size_bits: model_calculations.QuantizationBitSizes,
        token_count: int,
        batch_size: int = 1,
        software_buffer_multiplier: float = 1.15
) -> float:
    parameter_count = parameter_count_billions * 1e9

    model_size_bytes = model_calculations.model_size_bytes_calculation(
        parameter_count,
        quantization_size_bits
    )

    model_inference_activation_size_bytes = model_calculations.model_inference_activation_size_bytes_calculation(
        model_size_bytes
    )

    hidden_size, number_of_layers = model_calculations.hidden_dimension_and_number_of_layers_from_parameter_count(
        parameter_count
    )

    key_value_cache_per_token_size_bytes = model_calculations.key_value_cache_per_token_size_bytes_calculation(
        hidden_size,
        quantization_size_bits,
        number_of_layers
    )

    key_value_cache_size_bytes = model_calculations.key_value_cache_size_bytes_calculation(
        batch_size,
        token_count,
        key_value_cache_per_token_size_bytes
    )

    model_size_with_tokens = model_size_bytes + model_inference_activation_size_bytes + key_value_cache_size_bytes

    return (model_size_with_tokens * software_buffer_multiplier) / (1024 ** 3)
