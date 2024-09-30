from dandy.contrib.bots import SingleChoiceLlmBot
from dandy.llm.prompt import Prompt
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1


class OceanSelectionLlmBot(SingleChoiceLlmBot):
    role_prompt = Prompt().text('You are an ocean selection bot.')
    llm_config = OLLAMA_LLAMA_3_1
    llm_temperature = 0.0
