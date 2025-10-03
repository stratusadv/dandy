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
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'qwen3-coder:30b',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'SMART': {
        'MODEL': 'gemma3:27b',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'SMART_FAST': {
        'MODEL': 'gemma3:12b',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'FAST': {
        'MODEL': 'gemma3:4b',
        'TEMPERATURE': 0.1,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'THINKING': {
        'MODEL': 'qwen3:235b',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'GPT_3_5_TURBO': {
        **OPEN_AI_CONFIG,
        'MODEL': 'gpt-3.5-turbo',
    },
    'GPT_4o_MINI': {
        **OPEN_AI_CONFIG,
        'MODEL': 'gpt-4o-mini',
    },
    'GPT_4o': {
        **OPEN_AI_CONFIG,
        'MODEL': 'gpt-4o',
    },
    'GPT_o3_MINI': {
        **OPEN_AI_CONFIG,
        'MODEL': 'o3-mini',
    },
}
