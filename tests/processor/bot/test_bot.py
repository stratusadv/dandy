from unittest import TestCase

from dandy.processor.processor import BaseProcessor
from tests.processor.bot.intelligence.intel import MoneyBagIntel
from tests.processor.bot.intelligence.bots import MoneyBagBot
from tests.llm.decorators import run_llm_configs


class TestBot(TestCase):
    def test_bot_import(self):
        from dandy.processor.bot.bot import Bot

        self.assertTrue(type(Bot) is type(BaseProcessor))

    @run_llm_configs()
    def test_bot_intel_class_include(self, llm_config: str):
        money_bag_bot = MoneyBagBot()
        money_bag_bot.llm_config = llm_config

        money_bag = money_bag_bot.process(
            user_input='I have 14 coins',
            intel_class=MoneyBagIntel,
            include={'coins'},
        )

        self.assertEqual(money_bag.coins, 14)
        self.assertEqual(money_bag.bills, None)
        self.assertEqual(money_bag.gems, None)

    @run_llm_configs()
    def test_bot_intel_class_exclude(self, llm_config: str):
        money_bag_bot = MoneyBagBot()
        money_bag_bot.llm_config = llm_config

        money_bag = money_bag_bot.process(
            # This commented prompt freezes or locks the llm in indefinite inference !!!
            # user_input='Please give me 22 coins and 17 gems.',
            user_input='I would love to have more gems and coins in for my personal value.',
            intel_class=MoneyBagIntel,
            exclude={
                'bills': True, 'gems': {
                    'quality': True
                }
            },
        )

        gems_value = 0

        if money_bag.gems is not None:
            for gem in money_bag.gems:
                gems_value = gem.value

        self.assertGreater(money_bag.coins, 0)
        self.assertEqual(money_bag.bills, None)
        self.assertGreater(gems_value, 0)

    @run_llm_configs()
    def test_bot_intel_object_include(self, llm_config: str):
        money_bag_bot = MoneyBagBot()
        money_bag_bot.llm_config = llm_config

        coins = 10
        bills = 50

        old_money_bag = MoneyBagIntel(
            coins=coins,
            bills=bills
        )

        additional_coins = 15

        new_money_bag = money_bag_bot.process(
            user_input=f'I have {coins} coins can you please add {additional_coins} more?',
            intel_object=old_money_bag,
            include={'coins'},
        )

        self.assertEqual(new_money_bag.coins, coins + additional_coins)
        self.assertEqual(new_money_bag.bills, bills)
        self.assertEqual(new_money_bag.gems, None)

    def test_bot_options_init(self):
        money_bag_bot = MoneyBagBot(llm_temperature=0.5)

