from abc import ABC, abstractmethod

from dandy.connector.connector import BaseConnector


class BaseLlmConnector(ABC, BaseConnector):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        raise NotImplementedError