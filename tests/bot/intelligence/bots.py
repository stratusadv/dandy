from pydantic.main import IncEx
from typing import Union, Type

from dandy.processor.bot.bot import Bot
from dandy.llm.prompt.prompt import Prompt
from tests.bot.intelligence.intel import MoneyBagIntel


class MoneyBagBot(Bot):
    def process(
            self,
            user_input: str,
            intel_class: Union[Type[MoneyBagIntel], None] = None,
            intel_object: Union[MoneyBagIntel, None] = None,
            include: Union[IncEx, None] = None,
            exclude: Union[IncEx, None] = None,
    ) -> MoneyBagIntel:
        return self.llm.prompt_to_intel(
            prompt=Prompt(user_input),
            intel_class=intel_class,
            intel_object=intel_object,
            include_fields=include,
            exclude_fields=exclude,
        )
