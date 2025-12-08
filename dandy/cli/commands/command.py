from abc import ABC, abstractmethod


class BaseCommand(ABC):
    name: str
    description: str
    calls: tuple[str, ...]

    def __post_init__(self):
        check_attrs = ['name', 'description', 'calls']
        for attr in check_attrs:
            if not hasattr(self, attr):
                message = f'Command `{attr}` is required'
                raise ValueError(message)

    @abstractmethod
    def help(self):
        raise NotImplementedError

    @classmethod
    @property
    def input_calls(cls) -> list[str]:
        return [f'/{call}' for call in cls.calls]

    def run(self):
        raise NotImplementedError
