import time
import uuid
from time import sleep
from unittest import TestCase

from typing import Callable

from dandy.cache.memory.decorators import cache_to_memory
from dandy.cache.sqlite.decorators import cache_to_sqlite
from dandy.cache.cache import BaseCache
from tests.cache.intelligence.caches import CACHE_LIMIT, sql_lite_cache, memory_cache
from tests.cache.intelligence.intel import ClownIntel, WigIntel, CandyNotIntel


class TestCache(TestCase):
    @classmethod
    def tearDownClass(cls):
        sql_lite_cache.clear()
        sql_lite_cache.destroy_all()
        memory_cache.destroy_all()

    def run_test_cache(self, cache: BaseCache, cache_decorator: Callable):
        cache.clear()

        @cache_decorator(limit=CACHE_LIMIT)
        def create_clown(name: str, juggles: bool, wig_color: str) -> ClownIntel:
            sleep(0.5)

            return ClownIntel(name=name, juggles=juggles, wig=WigIntel(color=wig_color))

        start = time.perf_counter()

        clown = create_clown(name="Happy Fred", juggles=True, wig_color="red")

        self.assertGreater(time.perf_counter() - start, 0.5)

        cached_start = time.perf_counter()

        _ = create_clown(name="Happy Fred", juggles=True, wig_color="red")
        cached_clown = create_clown(name="Happy Fred", juggles=True, wig_color="red")
        _ = create_clown(name="Happy Fred", juggles=True, wig_color="red")

        self.assertLess(time.perf_counter() - cached_start, 0.1)

        self.assertEqual(clown, cached_clown)

    def test_memory_cache(self):
        self.run_test_cache(memory_cache, cache_to_memory)

    def test_sqlite_cache(self):
        self.run_test_cache(sql_lite_cache, cache_to_sqlite)

    def run_text_cache_limit(self, cache: BaseCache, cache_decorator: Callable):
        cache.clear()


        @cache_decorator(limit=CACHE_LIMIT)
        def create_clown(name: str, juggles: bool, wig_color: str) -> ClownIntel:
            return ClownIntel(name=name, juggles=juggles, wig=WigIntel(color=wig_color))

        for _ in range(int(CACHE_LIMIT * 2)):
            create_clown(name=str(uuid.uuid4()), juggles=True, wig_color=str(uuid.uuid4()))

        self.assertLess(len(cache), int(CACHE_LIMIT * 1.5))

    def test_memory_cache_limit(self):
        self.run_text_cache_limit(memory_cache, cache_to_memory)

    def test_sqlite_cache_limit(self):
        self.run_text_cache_limit(sql_lite_cache, cache_to_sqlite)

    def run_complex_object_cache(self, cache: BaseCache, cache_decorator: Callable):
        cache.clear()

        @cache_decorator(limit=CACHE_LIMIT * 3)
        def create_candy(candy: CandyNotIntel) -> CandyNotIntel:
            return CandyNotIntel(sweetness=candy.sweetness)

        for _ in range(3):
            for i in range(CACHE_LIMIT):
                _ = create_candy(CandyNotIntel(sweetness=i))

        self.assertEqual(CACHE_LIMIT, len(cache))

    # Todo: Broken Right now
    # def test_memory_complex_object_cache(self):
    #     self.run_complex_object_cache(memory_cache, cache_to_memory)
    #
    # def test_sqlite_complex_object_cache(self):
    #     self.run_complex_object_cache(sql_lite_cache, cache_to_sqlite)

