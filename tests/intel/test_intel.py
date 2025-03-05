import json
from typing import Union
from unittest import TestCase

from dandy.intel import BaseIntel
from dandy.intel.exceptions import IntelException


class Thing(BaseIntel):
    name: str
    description: str | None = None


class Bag(BaseIntel):
    color: str
    stylish: bool
    things: list[Thing]


class Person(BaseIntel):
    first_name: str
    last_name: str
    middle_name: Union[str, None] = None
    age: int | None = None
    bag: Bag | None = None


class TestIntel(TestCase):
    def test_intel(self):
        class TestingIntel(BaseIntel):
            pass

        intel = TestingIntel()
        self.assertIsInstance(intel, TestingIntel)

    def test_intel_include_and_exclude_json_schema(self):
        try:
            _ = Person.model_inc_ex_class_copy(include={'middle_name'}, exclude={'first_name'})

        except IntelException:
            self.assertTrue(True)

    def test_intel_include_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(include={'middle_name'})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('first_name', json_schema['properties'])

    def test_intel_include_deep_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(include={'middle_name': True, 'bag': {'color': True}})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('first_name', json_schema['properties'])
        self.assertNotIn('stylish', json_schema['$defs']['Bag']['properties'])

    def test_intel_include_deeper_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(include={'middle_name': True, 'bag': {'stylish': True, 'things': {'description': True}}})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('first_name', json_schema['properties'])
        self.assertNotIn('color', json_schema['$defs']['Bag']['properties'])
        self.assertNotIn('name', json_schema['$defs']['Thing']['properties'])

    def test_intel_exclude_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(exclude={'middle_name'})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])

    def test_intel_exclude_deep_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(exclude={'middle_name': True, 'bag': {'color': True}})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('color', json_schema['$defs']['Bag']['properties'])

    def test_intel_exclude_deeper_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(exclude={'middle_name': True, 'bag': {'color': True, 'things': {'description': True}}})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('color', json_schema['$defs']['Bag']['properties'])
        self.assertNotIn('description', json_schema['$defs']['Thing']['properties'])

