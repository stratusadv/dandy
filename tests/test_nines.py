from random import randint
from unittest import TestCase

from tests.decorators import nines_testing

class TestNines(TestCase):
    def test_nines(self):
        @nines_testing(3)
        def multiply(x: int, y: int) -> int:
            multiply.call_count += 1
            return x * y

        multiply.call_count = 0

        multiply(randint(0,100), randint(0,100))

        self.assertEqual(multiply.call_count, 1000)
