from dandy.contrib.bots import SingleChoiceLlmBot
from dandy.llm.prompt import Prompt
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1_8B


class OceanSelectionLlmBot(SingleChoiceLlmBot):
    role_prompt = Prompt().text('You are an ocean selection bot.')
    config = OLLAMA_LLAMA_3_1_8B
    temperature = 0.0
