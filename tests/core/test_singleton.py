from unittest import TestCase

from dandy.core.singleton import Singleton

class TestSingleton(TestCase):
    def test_singleton(self):
        class PersonSingleton(Singleton):
            pass

        person_1 = PersonSingleton()

        person_2 = PersonSingleton()

        self.assertEqual(id(person_1), id(person_2))