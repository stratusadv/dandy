import os
from pathlib import Path


ALLOW_DEBUG_RECORDING = True

BASE_PATH = Path.resolve(Path(__file__)).parent

# Other DEFAULT Settings - See dandy.default_settings for all options

# DEFAULT_LLM_TEMPERATURE: Union[float, None] = 0.7
# DEFAULT_LLM_SEED: Union[int, None] = 77
# DEFAULT_LLM_RANDOMIZE_SEED: bool = False
# DEFAULT_LLM_MAX_INPUT_TOKENS: Union[int, None] = 8000
# DEFAULT_LLM_MAX_OUTPUT_TOKENS: Union[int, None] = 4000
# DEFAULT_LLM_CONNECTION_RETRY_COUNT: int = 10
# DEFAULT_LLM_PROMPT_RETRY_COUNT: int = 2
# DEFAULT_LLM_REQUEST_TIMEOUT: Union[int, None] = None


LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'qwen2.5-coder:14b-instruct-q4_K_M',
        'TEMPERATURE': 0.0,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'LLAMA_3_1_8B': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'llama3.1:8b-instruct-q4_K_M',
    },
    'PHI_4_14B': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'phi4:14b-q4_K_M',
    },
}