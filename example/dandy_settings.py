import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

DEBUG = os.getenv("DEBUG", "False") == "True"

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'gemma3:12b',
        'TEMPERATURE': 0.1,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'BASIC': {
        'MODEL': 'gemma3:4b',
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'ADVANCED': {
        'MODEL': 'gemma3:12b',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'COMPLEX': {
        'MODEL': 'gemma3:27b',
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
}