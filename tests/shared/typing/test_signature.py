from typing import List, Dict, Any
from unittest import TestCase

from dandy.shared.exceptions import DandyCriticalError
from dandy.shared.typing.exceptions import TypingCriticalError, TypingRecoverableError
from dandy.shared.typing.registry import resolve_type_from_registry
from dandy.shared.typing.typed_kwargs import TypedKwargs
from dandy.shared.typing.typing import TypedKwargsDict
from dandy.shared.typing.signature import (
    get_typed_kwargs_from_callable_signature,
    get_typed_kwargs_from_simple_json_schema,
    string_to_type_or_error,
)
from tests.shared.typing.consts import SIMPLE_JSON_SCHEMA


class TestTypingTools(TestCase):
    def test_typed_kwargs_from_simple_json_schema(self):
        typed_kwargs = get_typed_kwargs_from_simple_json_schema(
            simple_json_schema=SIMPLE_JSON_SCHEMA
        )

        self.assertEqual(typed_kwargs['first_name'], str)
        self.assertEqual(typed_kwargs['weight'], int)
        self.assertEqual(typed_kwargs['height'], float)

    def test_typed_kwargs_from_simple_json_schema_accepts_json_string(self) -> None:
        typed_kwargs = get_typed_kwargs_from_simple_json_schema('{"name": "str"}')

        self.assertEqual(typed_kwargs['name'], str)

    def test_typed_kwargs_from_simple_json_schema_maps_dict_and_list_types(self) -> None:
        typed_kwargs = get_typed_kwargs_from_simple_json_schema(
            {'mapping': {'str': 'int'}, 'items': ['str'], 'empty': []}
        )

        self.assertEqual(typed_kwargs['mapping'], Dict[str, int])
        self.assertEqual(typed_kwargs['items'], List[str])
        self.assertEqual(typed_kwargs['empty'], list)

    def test_typed_kwargs_from_simple_json_schema_unknown_type_raises(self) -> None:
        with self.assertRaises(TypingRecoverableError):
            get_typed_kwargs_from_simple_json_schema({'name': 'not-a-type'})

    def test_typed_kwargs_from_callable_signature(self) -> None:
        def sample_function(required: str, defaulted: int = 5, defaulted_none: list = None):
            return required, defaulted, defaulted_none

        typed_kwargs = get_typed_kwargs_from_callable_signature(sample_function)

        self.assertEqual(typed_kwargs['required'], (str, ...))
        self.assertEqual(typed_kwargs['defaulted'], (int, 5))
        self.assertEqual(typed_kwargs['defaulted_none'], (list, None))

    def test_typed_kwargs_from_callable_signature_omits_defaults_when_disabled(self) -> None:
        def sample_function(required: str, defaulted: int = 5):
            return required, defaulted

        typed_kwargs = get_typed_kwargs_from_callable_signature(
            sample_function, return_defaulted=False
        )

        self.assertEqual(typed_kwargs['required'], (str, ...))
        self.assertNotIn('defaulted', typed_kwargs.data)

    def test_typed_kwargs_from_callable_signature_unannotated_parameter_raises(self) -> None:
        def sample_function(required: str, unannotated):
            return required, unannotated

        with self.assertRaises(TypingCriticalError):
            get_typed_kwargs_from_callable_signature(sample_function)

    def test_string_to_type_or_error(self) -> None:
        self.assertEqual(string_to_type_or_error('str'), str)
        self.assertEqual(string_to_type_or_error('INT'), int)
        self.assertEqual(string_to_type_or_error('Float'), float)
        self.assertEqual(string_to_type_or_error('number'), int)

        with self.assertRaises(TypingCriticalError):
            string_to_type_or_error('not-a-type')


class TestTypedKwargs(TestCase):
    def test_contains_rejects_non_typed_kwargs(self) -> None:
        typed_kwargs = TypedKwargs({'a': (str, ...)})

        with self.assertRaises(DandyCriticalError):
            _ = 'a' in typed_kwargs

    def test_contains_true_for_matching_sub_set(self) -> None:
        typed_kwargs = TypedKwargs({'a': (str, ...), 'b': (int, 5)})
        sub_typed_kwargs = TypedKwargs({'a': (str, ...)})

        self.assertIn(sub_typed_kwargs, typed_kwargs)

    def test_contains_false_when_not_a_sub_set(self) -> None:
        typed_kwargs = TypedKwargs({'a': (str, ...)})
        superset = TypedKwargs({'a': (str, ...), 'b': (int, 5)})

        self.assertNotIn(superset, typed_kwargs)

    def test_contains_false_when_types_differ(self) -> None:
        typed_kwargs = TypedKwargs({'a': (int, ...)})
        other = TypedKwargs({'a': (str, ...)})

        self.assertNotIn(other, typed_kwargs)

    def test_contains_resolves_string_types_from_registry(self) -> None:
        typed_kwargs = TypedKwargs({'a': (TypedKwargsDict, ...)})
        string_typed = TypedKwargs({'a': ('TypedKwargsDict', ...)})

        self.assertIn(string_typed, typed_kwargs)

    def test_contains_resolves_self_string_types_from_registry(self) -> None:
        typed_kwargs = TypedKwargs({'a': ('TypedKwargsDict', ...)})
        concrete_typed = TypedKwargs({'a': (TypedKwargsDict, ...)})

        self.assertIn(concrete_typed, typed_kwargs)


class TestResolveTypeFromRegistry(TestCase):
    def test_known_string_resolves_to_registered_type(self) -> None:
        self.assertIs(
            resolve_type_from_registry('TypedKwargsDict'),
            TypedKwargsDict,
        )

    def test_unknown_string_falls_back_to_any(self) -> None:
        self.assertIs(resolve_type_from_registry('not-a-registered-type'), Any)
