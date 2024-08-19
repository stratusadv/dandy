from enum import Enum


class LlmService(Enum):
    OLLAMA = 'ollama'
    OPENAI = 'openai'