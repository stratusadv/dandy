from unittest import TestCase

from pydantic import ValidationError

from dandy.domain.intel.intel import BaseIntel, DefaultIntel


class TestDefaultIntel(TestCase):
    def test_default_intel_stores_text(self) -> None:
        intel = DefaultIntel(text='some plain prose')

        self.assertEqual(intel.text, 'some plain prose')

    def test_default_intel_is_a_base_intel(self) -> None:
        self.assertIsInstance(DefaultIntel(text='x'), BaseIntel)

    def test_default_intel_str_returns_text(self) -> None:
        intel = DefaultIntel(text='hello world')

        self.assertEqual(str(intel), 'hello world')

    def test_default_intel_requires_text(self) -> None:
        with self.assertRaises(ValidationError):
            DefaultIntel()
