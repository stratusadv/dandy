import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

DEBUG = os.getenv("DEBUG", "False") == "True"

if DEBUG:
    from dandy.core.debug import *

# These defaults keep the test suite hermetic: hermetic (mocked) tests can build
# LLM configs without a live endpoint, while live-LLM tests still skip unless a
# real AI_API_KEY is exported (see tests/consts.py). Real env vars override them.
AI_API = {
    'HOST': os.getenv('AI_API_HOST', 'https://api.openai.com'),
    'PORT': int(os.getenv('AI_API_PORT', '443')),
    'API_KEY': os.getenv('AI_API_KEY', 'test-key'),
}

LLM_CONFIGS = {
    'DEFAULT': {
        **AI_API,
        'MODEL': os.getenv('LLM_DEFAULT_MODEL', 'gpt-test'),
        'OPTIONS': {
            'temperature': 0.7
        }
    },
    'THINKING': {
        'MODEL': os.getenv('LLM_THINKING_MODEL', 'gpt-test'),
        'OPTIONS': {
            'temperature': 0.4
        }
    },
    'AUDIO': {
        'MODEL': os.getenv('LLM_AUDIO_MODEL', 'gpt-test'),
    },
    'VISION': {
        'MODEL': os.getenv('LLM_VISION_MODEL', 'gpt-test'),
    },
}
