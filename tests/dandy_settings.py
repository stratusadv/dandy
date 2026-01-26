import os
from pathlib import Path

# from dandy.default_settings import AUDIO_CONFIGS

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

# AUDIO_CONFIGS = {
#     'DEFAULT': {
#         **AI_API,
#         'MODEL': os.getenv("AUDIO_DEFAULT_MODEL"),
#     },
# }

LLM_CONFIGS = {
    'DEFAULT': {
        **AI_API,
        'MODEL': os.getenv("LLM_DEFAULT_MODEL"),
    },
    'VISION': {
        'MODEL': os.getenv("VISION_DEFAULT_MODEL"),
    },
}
