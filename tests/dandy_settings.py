import os
from pathlib import Path

ALLOW_DEBUG_RECORDING = True

BASE_PATH = Path.resolve(Path(__file__)).parent

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
        'MODEL': 'qwen2.5-coder:14b-instruct-q4_K_M',
        'TEMPERATURE': 0.0,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'LLAMA_3_1_8B': {
        'MODEL': 'llama3.1:8b-instruct-q4_K_M',
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'PHI_4_14B': {
        'MODEL': 'phi4:14b-q4_K_M',
    },
    'DEEPSEEK_R1_14B': {
        'MODEL': 'deepseek-r1:14b',
    },
    'GEMMA_3_12B_VISION': {
        'MODEL': 'gemma3:12b',
    },
    'GEMMA_3_27B_VISION': {
        'MODEL': 'gemma3:27b',
    },
    'GPT_3_5_TURBO': {
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
}