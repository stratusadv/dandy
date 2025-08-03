from pydantic.main import IncEx
from typing import Union, Type

from dandy.llm import BaseLlmBot, Prompt
from tests.llm.bot.intel import MoneyBagIntel


class MoneyBagLlmBot(BaseLlmBot[MoneyBagIntel]):
    @classmethod
    def process(
            cls,
            user_input: str,
            intel_class: Union[Type[MoneyBagIntel], None] = None,
            intel_object: Union[MoneyBagIntel, None] = None,
            include: Union[IncEx, None] = None,
            exclude: Union[IncEx, None] = None,
    ) -> MoneyBagIntel:
        return cls.process_prompt_to_intel(
            prompt=Prompt(user_input),
            intel_class=intel_class,
            intel_object=intel_object,
            include_fields=include,
            exclude_fields=exclude,
        )
