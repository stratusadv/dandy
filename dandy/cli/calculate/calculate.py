from dandy.calculator.llm_calculator import model_size_and_token_count_for_inference_to_vram_gb

def calculate(
        model_parameter_count_billions: int,
        quantization_size_bits: int,
        token_count: int,
) -> float:

    return model_size_and_token_count_for_inference_to_vram_gb(
        model_parameter_count_billions,
        quantization_size_bits,
        token_count
    )
