import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

DEBUG = os.getenv("DEBUG", "False") == "True"

if DEBUG:
    from dandy.core.debug import *

OLLAMA_CONFIG = {
    'PORT': int(os.getenv('OLLAMA_PORT')),
    'API_KEY': os.getenv('OLLAMA_API_KEY'),
}

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_1_HOST"),
        **OLLAMA_CONFIG,
        'MODEL': 'qwen3:30b-instruct',
        'TEMPERATURE': 0.5,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'BASIC': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_1_HOST"),
        **OLLAMA_CONFIG,
        'MODEL': 'qwen3:30b-instruct',
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'ADVANCED': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_1_HOST"),
        **OLLAMA_CONFIG,
        'MODEL': 'qwen3:30b-instruct',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'COMPLEX': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_2_HOST"),
        **OLLAMA_CONFIG,
        'MODEL': 'qwen3:235b-instruct',
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
}
