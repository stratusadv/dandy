from unittest import TestCase


class TestSingleton(TestCase):
    def test_singleton_import(self):
        from dandy.core.singleton import Singleton
        Singleton()
