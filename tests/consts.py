import os

from unittest import skipUnless

TESTING_LLM_CONFIGS = ['DEFAULT']

_PLACEHOLDER_API_KEYS = {'test-key', 'changeme', 'your-api-key', 'placeholder'}

LIVE_LLM_AVAILABLE = (
    bool(os.getenv('AI_API_KEY'))
    and os.getenv('AI_API_KEY') not in _PLACEHOLDER_API_KEYS
)

live_llm_test = skipUnless(
    LIVE_LLM_AVAILABLE,
    'Requires a real AI_API_KEY.',
)
