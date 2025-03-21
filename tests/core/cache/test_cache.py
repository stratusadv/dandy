import time
import uuid
from time import sleep
from unittest import TestCase

from typing_extensions import Callable

from dandy.core.cache.cache import BaseCache
from dandy.core.cache import MemoryCache
from dandy.core.cache import cache_to_memory
from dandy.core.cache import SqliteCache
from dandy.core.cache import cache_to_sqlite
from dandy.intel import BaseIntel


class WigIntel(BaseIntel):
    color: str


class ClownIntel(BaseIntel):
    name: str
    juggles: bool
    wig: WigIntel


class Candy:
    def __init__(self, sweetness: int):
        self.sweetness = sweetness

test_limit = 100


sql_lite_cache = SqliteCache(
    cache_name='dandy',
    limit=test_limit
)

memory_cache = MemoryCache(
    cache_name='dandy',
    limit=test_limit
)


class TestCache(TestCase):
    @classmethod
    def tearDownClass(cls):
        sql_lite_cache.destroy()
        memory_cache.destroy()

    def run_test_cache(self, cache: BaseCache, cache_decorator: Callable):
        cache.clear()

        @cache_decorator(limit=test_limit)
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


        @cache_decorator(limit=test_limit)
        def create_clown(name: str, juggles: bool, wig_color: str) -> ClownIntel:
            return ClownIntel(name=name, juggles=juggles, wig=WigIntel(color=wig_color))

        for _ in range(int(test_limit * 2)):
            create_clown(name=str(uuid.uuid4()), juggles=True, wig_color=str(uuid.uuid4()))

        self.assertLess(len(cache), int(test_limit * 1.5))

    def test_memory_cache_limit(self):
        self.run_text_cache_limit(memory_cache, cache_to_memory)

    def test_sqlite_cache_limit(self):
        self.run_text_cache_limit(sql_lite_cache, cache_to_sqlite)

    def run_complex_object_cache(self, cache: BaseCache, cache_decorator: Callable):
        cache.clear()

        @cache_decorator(limit=test_limit * 3)
        def create_candy(candy: Candy) -> Candy:
            return Candy(sweetness=candy.sweetness)

        for _ in range(3):
            for i in range(test_limit):
                _ = create_candy(Candy(sweetness=i))

        self.assertEqual(test_limit, len(cache))

    def test_memory_complex_object_cache(self):
        self.run_complex_object_cache(memory_cache, cache_to_memory)

    def test_sqlite_complex_object_cache(self):
        self.run_complex_object_cache(sql_lite_cache, cache_to_sqlite)

