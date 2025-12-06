from abc import ABC, abstractmethod


class BaseCommand(ABC):
    name: str
    calls: list[str]

    def __post_init__(self):
        if not self.name:
            message = 'Command `name` is required'
            raise ValueError(message)
        
        if not self.calls:
            message = 'Command `calls` is required'
            raise ValueError(message)

    @abstractmethod
    def help(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError