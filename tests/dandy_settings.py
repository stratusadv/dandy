import os
from pathlib import Path
from typing import Union

# This is used for controlling the debug recorder in development and should be set to false in production

ALLOW_DEBUG_RECORDING = True

# You should set this to the root directory of your project the default will be the current working directory

BASE_PATH = Path.resolve(Path(__file__)).parent

# These will override the default settings in the dandy settings module

# DEFAULT_LLM_TEMPERATURE: float = 0.7
# DEFAULT_LLM_SEED: int = 77
# DEFAULT_LLM_RANDOMIZE_SEED: bool = False
# DEFAULT_LLM_MAX_INPUT_TOKENS: int = 8000
# DEFAULT_LLM_MAX_OUTPUT_TOKENS: int = 4000
# DEFAULT_LLM_CONNECTION_RETRY_COUNT: int = 10
# DEFAULT_LLM_PROMPT_RETRY_COUNT: int = 2
# DEFAULT_LLM_REQUEST_TIMEOUT: Union[int, None] = None

# These are some example LLM configs you may only need one of these, you must have a "DEFAULT" LLM config

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
        # the default "TYPE", "HOST", "PORT" AND "API_KEY" from the "DEFAULT" config will flow to this config

        'MODEL': 'llama3.1:8b-instruct-q4_K_M',

        # You can override any of the default settings for each LLM config
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'PHI_4_14B': {
        'MODEL': 'phi4:14b-q4_K_M',
    },
    'DEEPSEEK_R1_14B': {
        'MODEL': 'deepseek-r1:14b',
    },
    'GEMMA_3_12B_VISION': {
        'MODEL': 'gemma3:12b',
    },
    'GPT_3_5_TURBO': {
        'TYPE': 'openai',
        'HOST': os.getenv("OPENAI_HOST"),
        'PORT': int(os.getenv("OPENAI_PORT", 443)),
        'API_KEY': os.getenv("OPEN_API_KEY"),
        'MODEL': 'gpt-3.5-turbo',
    },
}