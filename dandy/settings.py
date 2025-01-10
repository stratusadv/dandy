import os
from pathlib import Path
from typing import Union


BASE_PATH: Union[Path, str] = Path.cwd()

DEFAULT_LLM_TEMPERATURE: Union[float, None] = 0.7
DEFAULT_LLM_SEED: Union[int, None] = 77
DEFAULT_LLM_RANDOMIZE_SEED: bool = False
DEFAULT_LLM_MAX_INPUT_TOKENS: Union[int, None] = 8000
DEFAULT_LLM_MAX_OUTPUT_TOKENS: Union[int, None] = 4000

CONNECTION_RETRY_COUNT: int = 10
PROMPT_RETRY_COUNT: int = 2

LLM_CONFIGS = {
    # 'DEFAULT': {
    #     'TYPE': 'ollama',
    #     'HOST': os.getenv("OLLAMA_HOST"),
    #     'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
    #     'API_KEY': os.getenv("OLLAMA_API_KEY"),
    #     'MODEL': 'llama3.1:8b-instruct-q4_K_M',
    #     'TEMPERATURE': 0.5,
    #     'SEED': 77,
    #     'RANDOMIZE_SEED': False,
    #     'MAX_INPUT_TOKENS': 8000,
    #     'MAX_OUTPUT_TOKENS': 4000
    # },
}
