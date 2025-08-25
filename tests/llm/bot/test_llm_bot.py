from unittest import TestCase

from dandy.core.processor.processor import BaseProcessor
from tests.llm.bot.intel import MoneyBagIntel
from tests.llm.bot.llm_bots import MoneyBagLlmBot
from tests.llm.decorators import run_llm_configs


class TestLlmBot(TestCase):
    def test_llm_bot_import(self):
        from dandy.bot.bot import Bot

        self.assertTrue(type(Bot) is type(BaseProcessor))

    @run_llm_configs()
    def test_llm_bot_intel_class_include(self, llm_config: str):
        MoneyBagLlmBot().llm_config = llm_config

        money_bag = MoneyBagLlmBot().process(
            user_input='I have 14 coins',
            intel_class=MoneyBagIntel,
            include={'coins'},
        )

        self.assertEqual(money_bag.coins, 14)
        self.assertEqual(money_bag.bills, None)
        self.assertEqual(money_bag.gems, None)

    @run_llm_configs()
    def test_llm_bot_intel_class_exclude(self, llm_config: str):
        MoneyBagLlmBot().llm_config = llm_config

        money_bag = MoneyBagLlmBot().process(
            user_input='Make me rich with by giving me good number of gems and coins in my bag!',
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
        MoneyBagLlmBot().llm_config = llm_config

        coins = 10
        bills = 50
        
        old_money_bag = MoneyBagIntel(
            coins=coins,
            bills=bills
        )

        additional_coins = 15

        new_money_bag = MoneyBagLlmBot().process(
            user_input=f'I have {coins} coins can you please add {additional_coins} more?',
            intel_object=old_money_bag,
            include={'coins'},
        )

        self.assertEqual(new_money_bag.coins, coins + additional_coins)
        self.assertEqual(new_money_bag.bills, bills)
        self.assertEqual(new_money_bag.gems, None)

