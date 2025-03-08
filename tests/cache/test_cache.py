import time
from time import sleep
from unittest import TestCase

from dandy.cache.memory.cache import memory_cache
from dandy.cache.memory.decorators import cache_to_memory
from dandy.cache.sqlite.cache import sqlite_cache
from dandy.cache.sqlite.decorators import cache_to_sqlite
from dandy.intel import BaseIntel


class WigIntel(BaseIntel):
    color: str

class ClownIntel(BaseIntel):
    name: str
    juggles: bool
    wig: WigIntel


class TestCache(TestCase):
    def test_memory_cache(self):
        memory_cache.clear()
        
        @cache_to_memory
        def create_clown(name: str, juggles: bool, wig_color: str) -> ClownIntel:
            sleep(0.5)

            return ClownIntel(name=name, juggles=juggles, wig=WigIntel(color=wig_color))

        start = time.perf_counter()
        
        clown = create_clown(name="Happy Fred", juggles=True, wig_color="red")
        
        self.assertGreater(time.perf_counter() - start, 0.5)
        
        cached_start = time.perf_counter()

        cached_clown_1 = create_clown(name="Happy Fred", juggles=True, wig_color="red")
        cached_clown_2 = create_clown(name="Happy Fred", juggles=True, wig_color="red")
        cached_clown_3 = create_clown(name="Happy Fred", juggles=True, wig_color="red")

        self.assertLess(time.perf_counter() - cached_start, 0.1)
        
        self.assertEqual(clown, cached_clown_2)

    def test_sqlite_cache(self):
        sqlite_cache.clear()
        
        @cache_to_sqlite
        def create_clown(name: str, juggles: bool, wig_color: str) -> ClownIntel:
            sleep(0.5)

            return ClownIntel(name=name, juggles=juggles, wig=WigIntel(color=wig_color))

        start = time.perf_counter()

        clown = create_clown(name="Happy Fred", juggles=True, wig_color="red")

        self.assertGreater(time.perf_counter() - start, 0.5)

        cached_start = time.perf_counter()

        cached_clown_1 = create_clown(name="Happy Fred", juggles=True, wig_color="red")
        cached_clown_2 = create_clown(name="Happy Fred", juggles=True, wig_color="red")
        cached_clown_3 = create_clown(name="Happy Fred", juggles=True, wig_color="red")

        self.assertLess(time.perf_counter() - cached_start, 0.1)

        self.assertEqual(clown, cached_clown_2)

