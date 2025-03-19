from unittest import TestCase

from pydantic.main import IncEx
from typing_extensions import Union, List, Type

from dandy.intel import BaseIntel
from dandy.llm import BaseLlmBot, Prompt
from dandy.core.processor.processor import BaseProcessor
from tests.llm.decorators import run_llm_configs


class GemIntel(BaseIntel):
    name: str
    value: float
    quality: str | None = None


class MoneyBagIntel(BaseIntel):
    coins: int
    bills: int | None = None
    gems: Union[List[GemIntel], None] = None


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


class TestLlmBot(TestCase):
    def test_llm_bot_import(self):
        from dandy.llm import BaseLlmBot

        self.assertTrue(type(BaseLlmBot) is type(BaseProcessor))

    @run_llm_configs()
    def test_llm_bot_intel_class_include(self, llm_config: str):
        MoneyBagLlmBot.config = llm_config

        money_bag = MoneyBagLlmBot.process(
            user_input='I have 10 coins',
            intel_class=MoneyBagIntel,
            include={'coins'},
        )

        self.assertEqual(money_bag.coins, 10)
        self.assertEqual(money_bag.bills, None)
        self.assertEqual(money_bag.gems, None)

    @run_llm_configs()
    def test_llm_bot_intel_class_exclude(self, llm_config: str):
        MoneyBagLlmBot.config = llm_config

        money_bag = MoneyBagLlmBot.process(
            user_input='make me rich with lots of coins and gems!',
            intel_class=MoneyBagIntel,
            exclude={'bills': True, 'gems': {'quality': True}},
        )

        gems_value = 0

        if money_bag.gems is not None:
            for gem in money_bag.gems:
                gems_value = gem.value

        self.assertGreater(money_bag.coins, 0)
        self.assertEqual(money_bag.bills, None)
        self.assertGreater(gems_value, 0)

    @run_llm_configs()
    def test_llm_bot_intel_object_include(self, llm_config: str):
        MoneyBagLlmBot.config = llm_config

        coins = 10
        bills = 50
        
        old_money_bag = MoneyBagIntel(coins=coins, bills=bills)

        additional_coins = 15

        new_money_bag = MoneyBagLlmBot.process(
            user_input=f'I have {coins} coins can you please add {additional_coins} more?',
            intel_object=old_money_bag,
            include={'coins'},
        )

        self.assertEqual(new_money_bag.coins, coins + additional_coins)
        self.assertEqual(new_money_bag.bills, bills)
        self.assertEqual(new_money_bag.gems, None)

