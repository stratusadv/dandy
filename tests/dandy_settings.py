import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

DEBUG = os.getenv("DEBUG", "False") == "True"

if DEBUG:
    from dandy.core.debug import *


OPEN_AI_CONFIG = {
    'TYPE': 'openai',
    'HOST': os.getenv("OPENAI_HOST"),
    'PORT': int(os.getenv("OPENAI_PORT", 443)),
    'API_KEY': os.getenv("OPENAI_API_KEY"),
}

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_1_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'qwen3:30b-instruct',
        'TEMPERATURE': 0.4,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'SMART': {
        'HOST': os.getenv("OLLAMA_2_HOST"),
        'MODEL': 'qwen3:235b',
        'TEMPERATURE': 0.4,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'OPEN_AI_API_MODEL': {
        **OPEN_AI_CONFIG,
        'MODEL': 'qwen3:30b-instruct',
    },
}
