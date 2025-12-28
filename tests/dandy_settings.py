import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

DEBUG = os.getenv("DEBUG", "False") == "True"

if DEBUG:
    from dandy.core.debug import *


LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': os.getenv("AI_API_HOST"),
        'PORT': int(os.getenv("AI_API_PORT", '443')),
        'API_KEY': os.getenv("AI_API_KEY"),
        'MODEL': os.getenv("LLM_DEFAULT_MODEL"),
    },
    'VISION': {
        'MODEL': os.getenv("LLM_VISION_MODEL"),
    },
}
