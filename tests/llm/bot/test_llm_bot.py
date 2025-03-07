from unittest import TestCase

from pydantic.main import IncEx
from typing_extensions import Union, List, Type

from dandy.intel import BaseIntel
from dandy.llm import BaseLlmBot, Prompt
from dandy.processor.processor import BaseProcessor


class Gem(BaseIntel):
    name: str
    value: float
    quality: str | None = None

class MoneyBag(BaseIntel):
    coins: int
    bills: int | None = None
    gems: Union[List[Gem], None] = None


class MoneyBagLlmBot(BaseLlmBot[MoneyBag]):
    @classmethod
    def process(
            cls,
            user_input: str,
            intel_class: Union[Type[MoneyBag], None] = None,
            intel_object: Union[MoneyBag, None] = None,
            include: Union[IncEx, None] = None,
            exclude: Union[IncEx, None] = None,
    ) -> MoneyBag:
        return cls.process_prompt_to_intel(
            prompt=Prompt(user_input),
            intel_class=intel_class,
            intel_object=intel_object,
            include_fields=include,
            exclude_fields=exclude,
        )


class TestLlmBot(TestCase):
    def test_llm_bot_import(self):
        from dandy.llm.bot import BaseLlmBot

        self.assertTrue(type(BaseLlmBot) is type(BaseProcessor))

    def test_llm_bot_include(self):
        money_bag = MoneyBagLlmBot.process(
            user_input='I have 10 coins',
            intel_class=MoneyBag,
            include={'coins'},
        )

        self.assertEqual(money_bag.coins, 10)
        self.assertEqual(money_bag.bills, None)
        self.assertEqual(money_bag.gems, None)

    def test_llm_bot_exclude(self):
        money_bag = MoneyBagLlmBot.process(
            user_input='make me rich with lots of coins and gems!',
            intel_class=MoneyBag,
            exclude={'bills': True, 'gems': {'quality': True}},
        )

        gems_value = 0

        for gem in money_bag.gems:
            gems_value = gem.value

        self.assertGreater(money_bag.coins, 0)
        self.assertEqual(money_bag.bills, None)
        self.assertGreater(gems_value, 0)

    def test_llm_bot_intel_object_include(self):
        coins = 10
        additional_coins = 15
        bills = 50
        
        old_money_bag = MoneyBag(coins=coins, bills=bills)
        
        new_money_bag = MoneyBagLlmBot.process(
            user_input=f'I have {coins} coins can you please add {additional_coins} more?',
            intel_object=old_money_bag,
            include={'coins'},
        )

        print(new_money_bag.model_dump())

        self.assertEqual(new_money_bag.coins, coins + additional_coins)
        self.assertEqual(new_money_bag.bills, bills)
        self.assertEqual(new_money_bag.gems, None)

