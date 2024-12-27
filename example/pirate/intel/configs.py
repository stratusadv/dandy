import os

from dandy.llm.config import OllamaLlmConfig, OpenaiLlmConfig


OLLAMA_LLAMA_3_2 = OllamaLlmConfig(
    host=os.getenv("OLLAMA_HOST"),
    port=int(os.getenv("OLLAMA_PORT", 11434)),
    api_key=os.getenv("OLLAMA_API_KEY"),
    model='llama3.2:3b-instruct-q4_K_M',
    temperature=1.0,
    prompt_retry_count=3,
)

OLLAMA_LLAMA_3_1 = OllamaLlmConfig(
    host=os.getenv("OLLAMA_HOST"),
    port=int(os.getenv("OLLAMA_PORT", 11434)),
    api_key=os.getenv("OLLAMA_API_KEY"),
    model='llama3.1:8b-instruct-q4_K_M',
    temperature=1.0,
    prompt_retry_count=3,
)

OPENAI_GPT_3_5_TURBO = OpenaiLlmConfig(
    host='https://api.openai.com',
    port=int(os.getenv("OPENAI_PORT", 443)),
    model='gpt-3.5-turbo',
    api_key=os.getenv("OPENAI_API_KEY"),
)
