from abc import ABC, abstractmethod

from blessed import Terminal


class BaseElement(ABC):
    def __init__(self, term: Terminal):
        self.term = term

    @abstractmethod
    def render(self):
        raise NotImplementedError


