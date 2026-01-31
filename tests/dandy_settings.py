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
    },
    'VISION': {
        'MODEL': os.getenv("VISION_DEFAULT_MODEL"),
    },
}
