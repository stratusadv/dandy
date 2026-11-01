import os
from pathlib import Path

BASE_PATH = Path(os.environ.get('HOME', '/tmp'))

LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': os.environ.get('AI_API_HOST', 'https://ai.api.lc.ca.stratusadv.com'),
        'PORT': 443,
        'API_KEY': os.environ.get('AI_API_KEY', ''),
        'MODEL': 'stratus.thinking',
        'CONTEXT_SIZE': 228000,
    }
}

DEBUG = False
