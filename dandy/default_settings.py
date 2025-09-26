import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE: bool = False

BASE_PATH: Path | str = Path.cwd()

CACHE_MEMORY_LIMIT: int = 1000
CACHE_SQLITE_DATABASE_PATH: Path | str = BASE_PATH
CACHE_SQLITE_LIMIT: int = 10000

DEBUG: bool = False

AGENT_DEFAULT_PLAN_TIME_LIMIT_SECONDS: int | None = 600
AGENT_DEFAULT_PLAN_TASK_COUNT_LIMIT: int | None = 100

HTTP_CONNECTION_RETRY_COUNT: int = 10
HTTP_CONNECTION_TIMEOUT_SECONDS: int | None = None

LLM_DEFAULT_MAX_INPUT_TOKENS: int = 8000
LLM_DEFAULT_MAX_OUTPUT_TOKENS: int = 4000
LLM_DEFAULT_PROMPT_RETRY_COUNT: int | None = 2
LLM_DEFAULT_RANDOMIZE_SEED: bool = False
LLM_DEFAULT_REQUEST_TIMEOUT: int | None = None
LLM_DEFAULT_SEED: int = 77
LLM_DEFAULT_TEMPERATURE: float = 0.7

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'a_model:9b',
        'TEMPERATURE': 0.5,
        'SEED': 77,
        'RANDOMIZE_SEED': False,
        'MAX_INPUT_TOKENS': 8000,
        'MAX_OUTPUT_TOKENS': 4000
    },
}