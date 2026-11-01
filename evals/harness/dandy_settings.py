from pathlib import Path

BASE_PATH = Path('/workdir')

LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': 'http://127.0.0.1',
        'PORT': 8787,
        'API_KEY': 'eval-proxy',
        'MODEL': 'stratus.turbo',
        'CONTEXT_SIZE': 48000,
    }
}

CLI_CONFIG = {'CODING': 'DEFAULT'}

DEBUG = False
ALLOW_RECORDING_TO_FILE = True
