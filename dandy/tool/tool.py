from abc import ABC


class BaseTool(ABC):
    def __init__(self) -> None:
        if not self.setup():
            print(f"Failed to setup {self.__class__.__name__}")

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    def setup(self) -> None:
        raise NotImplementedError