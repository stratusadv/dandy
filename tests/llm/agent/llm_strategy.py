from dandy.llm.bot.llm_bot import LlmBot
from dandy.llm.agent.llm_strategy import BaseLlmAgentStrategy
from tests.llm.agent.llm_bots import MuseumEmailFinderBot


class MuseumEmailLlmStrategy(BaseLlmAgentStrategy):
    bots = [
        LlmBot,
        MuseumEmailFinderBot,
    ]