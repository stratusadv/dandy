from abc import ABC
from typing import Any, Self

from dandy.core.future.tools import process_to_future

from dandy.core.future.future import AsyncFuture

from dandy.bot.recorder import record_process_wrapper
from dandy.file.service import FileService

# from dandy.audio.mixin import AudioServiceMixin
from dandy.file.mixin import FileServiceMixin
from dandy.http.mixin import HttpServiceMixin
from dandy.http.service import HttpService
from dandy.intel.intel import BaseIntel
from dandy.intel.mixin import IntelServiceMixin
from dandy.llm.mixin import LlmServiceMixin
from dandy.llm.prompt.typing import PromptOrStr
# from dandy.bot.bot.mixin import BotServiceMixin
# from dandy.bot.base import BaseBot
from dandy.llm.service import LlmService


# from dandy.vision.mixin import VisionServiceMixin


class Bot(
    # AudioServiceMixin,
    # BaseBot,
    # BotServiceMixin,
    FileServiceMixin,
    LlmServiceMixin,
    HttpServiceMixin,
    IntelServiceMixin,
    # VisionServiceMixin,
):
    # description: str | None = 'Generic Bot for performing generic tasks'

    def __init__(
            self,
            **kwargs
    ):
        super().__init__()

        self._recorder_event_id = ''

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
                        name == "process"
                        and callable(attr)
                        and not hasattr(attr, "_wrapped")
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

    # def __init__(
    #     self,
    #     llm_config: str | None = None,
    #     llm_randomize_seed: bool | None = None,
    #     llm_seed: int | None = None,
    #     llm_temperature: float | None = None,
    #     **kwargs,
    # ):
    #     super().__init__(**kwargs)
    #
    #     self.get_llm_options().update_values(
    #         randomize_seed=llm_randomize_seed,
    #         seed=llm_seed,
    #         temperature=llm_temperature,
    #     )

    def process(
        self,
        *args,
        **kwargs,
    ) -> Any:
        if len(args) >= 1 and isinstance(args[0], PromptOrStr):
            kwargs['prompt'] = args[0]

        if len(args) == 2 and issubclass(args[1], BaseIntel):
            kwargs['intel_class'] = args[1]

        if 'prompt' in kwargs:
            return self.llm.prompt_to_intel(**kwargs)

        message = '`Bot.process` requires key word argument `prompt`.'
        raise ValueError(message)

    def process_to_future(self, *args, **kwargs) -> AsyncFuture:
        return process_to_future(self.process, *args, **kwargs)

