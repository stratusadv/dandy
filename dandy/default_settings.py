import os
from pathlib import Path

AGENT_DEFAULT_PLAN_TIME_LIMIT_SECONDS: int | None = 600
AGENT_DEFAULT_PLAN_TASK_COUNT_LIMIT: int | None = 100

ALLOW_RECORDING_TO_FILE: bool = False

BASE_PATH: Path | str = Path.cwd()

CACHE_MEMORY_LIMIT: int = 1000
CACHE_SQLITE_DATABASE_PATH: Path | str = BASE_PATH
CACHE_SQLITE_LIMIT: int = 10000

DANDY_DIRECTORY = '.dandy'

DEBUG: bool = False

FUTURES_MAX_WORKERS: int = 10

HTTP_CONNECTION_RETRY_COUNT: int = 4
HTTP_CONNECTION_TIMEOUT_SECONDS: int | None = 60

LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': os.getenv("AI_API_HOST"),
        'PORT': int(os.getenv("AI_API_POST", 443)),
        'API_KEY': os.getenv("AI_API_KEY"),
        'MODEL': os.getenv("AI_API_MODEL"),
        'OPTIONS': {
            'frequency_penalty': None,
            'max_completion_tokens': None,
            'presence_penalty': None,
            'temperature': None,
            'top_p': None,
        }
    },
}
