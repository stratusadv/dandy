from dandy.core.singleton import Singleton
from dandy.llm.config.config import LlmConfig


class Config(Singleton):
    llm = LlmConfig()