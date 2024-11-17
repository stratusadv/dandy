import os

from dandy.llm.config import OllamaLlmConfig


DEFAULT_LLM_CONFIG = OllamaLlmConfig(
    host=os.getenv("OLLAMA_HOST"),
    port=int(os.getenv("OLLAMA_PORT", 11434)),
    model='qwen2.5-coder:32b-instruct-q4_K_M',
    temperature=0.0,
    prompt_retry_count=3,
    context_length=8192,
    max_completion_tokens=2048
)