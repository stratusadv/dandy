from abc import ABC
from typing import Any, Self

from dandy.llm.prompt.prompt import Prompt
from dandy.bot.recorder import record_process_wrapper
from dandy.core.future.future import AsyncFuture
from dandy.core.future.tools import process_to_future
from dandy.file.mixin import FileServiceMixin
from dandy.http.mixin import HttpServiceMixin
from dandy.intel.mixin import IntelServiceMixin
from dandy.llm.mixin import LlmServiceMixin


class Bot(
    FileServiceMixin,
    LlmServiceMixin,
    HttpServiceMixin,
    IntelServiceMixin,
):
    def __init__(
            self,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.recorder_event_id = ''

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.__post_init__()

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:
            # Typing Does not work properly for processors if you override __getattribute__ in the BaseProcessor class.
            # This is a workaround and should be fixed in future versions of the python lsp.
            def __getattribute__(self: Self, name: str) -> Any:  # noqa: N807
                attr = super().__getattribute__(name)

                if (
                        name == 'process'
                        and callable(attr)
                        and not hasattr(attr, '_wrapped')
                ):
                    wrapped = record_process_wrapper(self, attr)
                    wrapped._wrapped = True
                    return wrapped

                return attr

            cls.__getattribute__ = __getattribute__

    def __post_init__(self):  # noqa: B027
        pass

    @classmethod
    def get_description(cls) -> str | None:
        pass

    def process(
            self,
            *args,
            **kwargs,
    ) -> Any:
        if len(args) >= 1 and isinstance(args[0], Prompt | str):
            kwargs['prompt'] = args[0]

        if 'prompt' in kwargs:
            return self.llm.prompt_to_intel(**kwargs)

        message = '`Bot.process` requires `prompt` as an argument.'
        raise ValueError(message)

    def process_to_future(self, *args, **kwargs) -> AsyncFuture:
        return process_to_future(self.process, *args, **kwargs)

    def reset(self):
        super().reset()
