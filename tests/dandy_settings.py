import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

DEBUG = os.getenv("DEBUG", "False") == "True"

if DEBUG:
    from dandy.core.debug import *


AI_API_CONFIG = {
    'TYPE': 'openai',
    'HOST': os.getenv("AI_API_HOST"),
    'PORT': int(os.getenv("AI_API_PORT", '443')),
    'API_KEY': os.getenv("AI_API_KEY"),
}

LLM_CONFIGS = {
    'DEFAULT': {
        **AI_API_CONFIG,
        'MODEL': 'stratus.smart',
        'TEMPERATURE': 0.2,
        # 'MAX_INPUT_TOKENS': 16000,
        # 'MAX_OUTPUT_TOKENS': 16000,
    },
    'QUICK': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_1_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", '11434')),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'qwen3:30b-instruct',
        'TEMPERATURE': 0.2,
        # 'MAX_INPUT_TOKENS': 16000,
        # 'MAX_OUTPUT_TOKENS': 16000,
    },
    'SMART': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_2_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", '11434')),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'qwen3:235b-instruct',
        'TEMPERATURE': 0.2,
        # 'MAX_INPUT_TOKENS': 16000,
        # 'MAX_OUTPUT_TOKENS': 16000,
    },
    'OPEN_AI_API_MODEL': {
        **AI_API_CONFIG,
        'MODEL': 'stratus.smart',
    },
}
