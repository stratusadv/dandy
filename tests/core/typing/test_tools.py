from unittest import TestCase

from dandy.core.typing.tools import get_typed_kwargs_from_simple_json_schema
from tests.core.typing.consts import SIMPLE_JSON_SCHEMA


class TestTypingTools(TestCase):
    def test_typed_kwargs_from_simple_json_schema(self):
        typed_kwargs = get_typed_kwargs_from_simple_json_schema(
            simple_json_schema=SIMPLE_JSON_SCHEMA
        )

        self.assertEqual(typed_kwargs['first_name'], str)
        self.assertEqual(typed_kwargs['weight'], int)
        self.assertEqual(typed_kwargs['height'], float)
