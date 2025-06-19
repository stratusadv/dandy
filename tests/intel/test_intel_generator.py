from unittest import TestCase

from dandy.intel import BaseListIntel
from dandy.intel.exceptions import IntelCriticalException
from dandy.intel.generator import IntelGenerator
from tests.intel.intel import ThingIntel, ThingsIntel


class TestIntelGenerator(TestCase):
    def test_intel_generator_from_callable_signature(self):
        def math(a: int, b: int) -> int:
            return a + b

        new_intel = IntelGenerator.intel_from_callable_signature(math)

        new_math_args = new_intel(
            a=1,
            b=2
        )

        self.assertEqual(math(**new_math_args.model_dump()), 3)

    def test_intel_generator_from_class_signature_no_annotations(self):
        with self.assertRaises(IntelCriticalException):
            def subtract(a, b):
                return a - b

            IntelGenerator.intel_from_callable_signature(subtract)
