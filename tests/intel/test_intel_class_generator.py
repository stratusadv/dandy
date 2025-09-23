import json
from unittest import TestCase

from pydantic import ValidationError

from dandy.core.typing.exceptions import TypingCriticalException
from dandy.intel.intel import BaseIntel
from dandy.intel.exceptions import IntelCriticalException
from dandy.intel.generator import IntelClassGenerator
from tests.core.typing.consts import SIMPLE_JSON_SCHEMA


class TestIntelClassGenerator(TestCase):
    def test_from_callable_signature(self):
        def math(a: int, b: int) -> int:
            return a + b

        new_intel_class = IntelClassGenerator.from_callable_signature(math)

        try:
            _ = new_intel_class(
                a=1,
                b='horse'
            )
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        new_math_args = new_intel_class(
            a=1,
            b=2
        )

        self.assertEqual(math(**new_math_args.model_to_kwargs()), 3)

    def test_from_complex_callable_signature(self):
        class Chaos(BaseIntel):
            x: int
            y: float

        def chaos_math(a: float, b: int, chaos_list: list[Chaos]) -> float:
            return a + b + sum((chaos.x + chaos.y for chaos in chaos_list))

        new_intel_class = IntelClassGenerator.from_callable_signature(chaos_math)

        try:
            _ = new_intel_class(
                a=1.0,
                b=1,
                chaos_list=[
                    Chaos(x=5, y=5.5),
                    Chaos(x=10, y='horse')
                ]
            )
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        new_chaos_math_args = new_intel_class(
            a=1.0,
            b=2,
            chaos_list=[
                Chaos(x=5, y=5.5),
                Chaos(x=10, y=10.5)
            ]
        )

        self.assertEqual(chaos_math(**new_chaos_math_args.model_to_kwargs()), 34.0)


    def test_from_class_signature_no_annotations(self):
        with self.assertRaises(TypingCriticalException):
            def subtract(a, b: int):
                return a - b

            IntelClassGenerator.from_callable_signature(subtract)

    def test_from_simple_json_schema(self):
        new_intel_class = IntelClassGenerator.from_simple_json_schema(
            json.dumps(SIMPLE_JSON_SCHEMA)
        )

        new_intel = new_intel_class(
            first_name='Phil',
            last_name='Jimerson',
            email='phil.jimerson@email.com',
            age=21,
            weight=147,
            height=80.5,
            friends=['Sarah', 'Larry', 'Rebecca'],
            cards={
                22: 'red',
                45: 'green'
            }
        )

        self.assertEqual(new_intel.first_name, 'Phil')
        self.assertEqual(new_intel.age, 21)
        self.assertEqual(new_intel.height, 80.5)
        self.assertEqual(new_intel.friends[1], 'Larry')
        self.assertEqual(new_intel.cards[45], 'green')
