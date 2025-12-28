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
        'TEMPERATURE': 0.2,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
}
