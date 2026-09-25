# dandy_settings.py

import os
from pathlib import Path

ALLOW_DEBUG_RECORDING = True

BASE_PATH = Path.resolve(Path(__file__)).parent

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'openai',
        'HOST': 'https://api.openai.com',
        'PORT': 443,
        'API_KEY': os.getenv('OPENAI_API_KEY'),
        'MODEL': 'gpt-4o-mini',
    }
}

# main.py

from dandy import Bot

response = Bot().process('What is the capital of Canada?')

print(response.text)

# Output: The capital of Canada is Ottawa
