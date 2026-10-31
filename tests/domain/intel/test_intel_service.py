from unittest import TestCase

from pydantic import ValidationError

from dandy.domain.intel.intel import BaseIntel, DefaultIntel
from dandy.domain.intel.service import IntelService
from tests.shared.typing.consts import SIMPLE_JSON_SCHEMA


def sample_handle(first_name: str, age: int = 30) -> str:
    return first_name


class TestIntelService(TestCase):
    def test_intel_class_from_callable_signature(self) -> None:
        intel_class = IntelService.intel_class_from_callable_signature(sample_handle)

        self.assertTrue(issubclass(intel_class, BaseIntel))

        intel_object = intel_class(first_name='Nathan', age=42)

        self.assertEqual(intel_object.first_name, 'Nathan')
        self.assertEqual(intel_object.age, 42)

    def test_intel_class_from_callable_signature_applies_defaults(self) -> None:
        intel_class = IntelService.intel_class_from_callable_signature(sample_handle)

        intel_object = intel_class(first_name='Nathan')

        self.assertEqual(intel_object.age, 30)

    def test_intel_class_from_simple_json_schema(self) -> None:
        intel_class = IntelService.intel_class_from_simple_json_schema(SIMPLE_JSON_SCHEMA)

        self.assertTrue(issubclass(intel_class, BaseIntel))

    def test_json_str_to_intel_object(self) -> None:
        intel_object = IntelService.json_str_to_intel_object(
            json_str='{"text": "parsed"}', intel=DefaultIntel
        )

        self.assertIsInstance(intel_object, DefaultIntel)
        self.assertEqual(intel_object.text, 'parsed')

    def test_json_str_to_intel_object_rejects_invalid_json(self) -> None:
        with self.assertRaises(ValidationError):
            IntelService.json_str_to_intel_object(json_str='not json at all', intel=DefaultIntel)

    def test_reset_is_a_noop(self) -> None:
        service = IntelService(obj=object())

        service.reset()
