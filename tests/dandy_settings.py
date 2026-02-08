import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

DEBUG = os.getenv("DEBUG", "False") == "True"

if DEBUG:
    from dandy.core.debug import *

AI_API = {
    'HOST': os.getenv("AI_API_HOST"),
    'PORT': int(os.getenv("AI_API_PORT", '443')),
    'API_KEY': os.getenv("AI_API_KEY"),
}

LLM_CONFIGS = {
    'DEFAULT': {
        **AI_API,
        'MODEL': os.getenv("LLM_DEFAULT_MODEL"),
        'OPTIONS': {
            'temperature': 0.7
        }
    },
    'THINKING': {
        'MODEL': os.getenv("LLM_THINKING_MODEL"),
        'OPTIONS': {
            'temperature': 0.4
        }
    },
    'AUDIO': {
        'MODEL': os.getenv("LLM_AUDIO_MODEL"),
    },
    'VISION': {
        'MODEL': os.getenv("LLM_VISION_MODEL"),
    },
}
