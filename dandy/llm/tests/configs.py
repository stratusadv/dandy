import os

from dandy.llm.config import LlmConfig


ollama_llama3_1_llm_config = LlmConfig(
    host=os.getenv("OLLAMA_HOST"),
    port=int(os.getenv("OLLAMA_PORT", 11434)),
    model='llama3.1',
    path_parameters=[
        'api',
        'chat',
    ]
)


openai_gpt3_5_turbo_llm_config = LlmConfig(
    host=os.getenv("OPENAI_HOST"),
    port=int(os.getenv("OPENAI_PORT", 443)),
    model='gpt-3.5-turbo',
    path_parameters=[
        'v1',
        'chat',
        'completions',
    ],
    api_key=os.getenv("OPENAI_API_KEY"),
)