from pathlib import Path

from typing_extensions import Union

ALLOW_RECORDING_TO_FILE: bool = False

BASE_PATH: Union[Path, str] = Path.cwd()

CACHE_MEMORY_LIMIT: int = 1000
CACHE_SQLITE_DATABASE_PATH: Union[Path, str] = BASE_PATH
CACHE_SQLITE_LIMIT: int = 10000

DEFAULT_LLM_TEMPERATURE: float = 0.7
DEFAULT_LLM_SEED: int = 77
DEFAULT_LLM_RANDOMIZE_SEED: bool = False
DEFAULT_LLM_MAX_INPUT_TOKENS: int = 8000
DEFAULT_LLM_MAX_OUTPUT_TOKENS: int = 4000
DEFAULT_LLM_PROMPT_RETRY_COUNT: int = 2
DEFAULT_LLM_REQUEST_TIMEOUT: Union[int, None] = None

HTTP_CONNECTION_RETRY_COUNT: int = 10

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
