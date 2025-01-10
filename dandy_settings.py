import os
from pathlib import Path

BASE_PATH = Path.resolve(Path(__file__)).parent

# Other DEFAULT Settings - See dandy/settings.py for all options

# DEFAULT_LLM_CONFIG = None
# DEFAULT_LLM_TEMPERATURE = 0.7
# DEFAULT_LLM_SEED = 77
# DEFAULT_LLM_RANDOMIZE_SEED = False
# DEFAULT_LLM_MAX_INPUT_TOKENS = 8000
# DEFAULT_LLM_MAX_OUTPUT_TOKENS = 4000

# CONNECTION_RETRY_COUNT = 10
# PROMPT_RETRY_COUNT = 2

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'llama3.1:8b-instruct-q4_K_M',
    },
}