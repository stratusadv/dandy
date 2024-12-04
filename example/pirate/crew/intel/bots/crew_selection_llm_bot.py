from dandy.contrib.bots import MultipleChoiceLlmBot
from dandy.llm.prompt import Prompt
from example.pirate.intel.configs import OLLAMA_LLAMA_3_1


class CrewSelectionLlmBot(MultipleChoiceLlmBot):
    role_prompt = Prompt().text('You are an pirate crew selection bot.')
    llm_config = OLLAMA_LLAMA_3_1
    llm_temperature = 0.0
