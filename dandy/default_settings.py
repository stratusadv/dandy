from pathlib import Path

ALLOW_RECORDING_TO_FILE: bool = False

BASE_PATH: Path | str = Path.cwd()

CACHE_MEMORY_LIMIT: int = 1000
CACHE_SQLITE_DATABASE_PATH: Path | str = BASE_PATH
CACHE_SQLITE_LIMIT: int = 10000

DEBUG: bool = False

# Use 0 to disable the limit on agents think time and thought count
DEFAULT_AGENT_PLAN_TIME_LIMIT_SECONDS: int = 600 # 10 minutes
DEFAULT_AGENT_PLAN_TASK_COUNT_LIMIT: int = 100 # This is per agent plan

DEFAULT_LLM_MAX_INPUT_TOKENS: int = 8000
DEFAULT_LLM_MAX_OUTPUT_TOKENS: int = 4000
DEFAULT_LLM_PROMPT_RETRY_COUNT: int = 2
DEFAULT_LLM_RANDOMIZE_SEED: bool = False
DEFAULT_LLM_REQUEST_TIMEOUT: int | None = None
DEFAULT_LLM_SEED: int = 77
DEFAULT_LLM_TEMPERATURE: float = 0.7

HTTP_CONNECTION_RETRY_COUNT: int = 10
HTTP_CONNECTION_TIMEOUT_SECONDS: int = 120

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
