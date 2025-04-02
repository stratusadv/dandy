import time
from unittest import TestCase

from typing_extensions import Callable

from dandy.cache import cache_to_memory
from dandy.cache import cache_to_sqlite
from dandy.cache.cache import BaseCache
from tests.core.cache.caches import sql_lite_cache, memory_cache

from tests.llm.bot.intel import MoneyBagIntel
from tests.llm.bot.llm_bots import MoneyBagLlmBot


class TestCacheWithLlm(TestCase):
    @classmethod
    def tearDownClass(cls):
        sql_lite_cache.destroy_all()
        memory_cache.destroy_all()

    def run_test_cache_with_llm_bot(self, cache: BaseCache, cache_decorator: Callable):
        cache.clear()

        class CachedMoneyBagLlmBot(MoneyBagLlmBot):
            @classmethod
            @cache_decorator()
            def process(cls, *args, **kwargs):
                return super().process(*args, **kwargs)

        start = time.perf_counter()

        _ = CachedMoneyBagLlmBot.process(
            user_input='I have 10 coins',
            intel_class=MoneyBagIntel,
            include={'coins'}
        )

        self.assertGreater(time.perf_counter() - start, 0.1)

        cached_start = time.perf_counter()

        money_bag = CachedMoneyBagLlmBot.process(
            user_input='I have 10 coins',
            intel_class=MoneyBagIntel,
            include={'coins'}
        )

        self.assertLess(time.perf_counter() - cached_start, 0.1)

        self.assertEqual(10, money_bag.coins)

    def test_memory_cache(self):
        self.run_test_cache_with_llm_bot(memory_cache, cache_to_memory)

    def test_sqlite_cache(self):
        self.run_test_cache_with_llm_bot(sql_lite_cache, cache_to_sqlite)

