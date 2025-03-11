import json
from typing import Union
from unittest import TestCase

from dandy.intel import BaseIntel
from dandy.intel.exceptions import IntelCriticalException


class Thing(BaseIntel):
    name: str
    description: str | None = None


class Bag(BaseIntel):
    color: str
    stylish: bool
    pockets: Union[int, None] = None
    things: Union[list[Thing], None] = None


class Person(BaseIntel):
    first_name: str
    last_name: str
    middle_name: Union[str, None] = None
    age: int | None = None
    bag: Union[Bag, None] = None


class TestIntel(TestCase):
    def test_intel(self):
        class TestingIntel(BaseIntel):
            pass

        intel = TestingIntel()
        self.assertIsInstance(intel, TestingIntel)

    def test_intel_include_invalid_field(self):
        try:
            _ = Person.model_inc_ex_class_copy(include={'height'})

        except IntelCriticalException:
            self.assertTrue(True)

    def test_intel_include_with_required_field(self):
        try:
            _ = Person.model_inc_ex_class_copy(include={'middle_name'})

        except IntelCriticalException:
            self.assertTrue(True)
            
    def test_intel_exclude_with_required_field(self):
        try:
            _ = Person.model_inc_ex_class_copy(exclude={'first_name'})

        except IntelCriticalException:
            self.assertTrue(True)

    def test_intel_include_and_exclude(self):
        try:
            _ = Person.model_inc_ex_class_copy(include={'middle_name'}, exclude={'first_name'})

        except IntelCriticalException:
            self.assertTrue(True)

    def test_intel_include_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(include={'first_name', 'last_name'})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])

    def test_intel_include_deep_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(
            include={'first_name': True, 'last_name': True, 'bag': {'color': True, 'stylish': True}}
        )

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('things', json_schema['$defs']['Bag']['properties'])

    def test_intel_include_deeper_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(
            include={'first_name': True, 'last_name': True, 'bag': {'color': True, 'stylish': True, 'things': {'name': True}}}
        )

        json_schema = PersonCopy.model_json_schema()
        
        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('pockets', json_schema['$defs']['Bag']['properties'])
        self.assertNotIn('description', json_schema['$defs']['Thing']['properties'])

    def test_intel_exclude_invalid_field(self):
        try:
            _ = Person.model_inc_ex_class_copy(exclude={'height'})

        except IntelCriticalException:
            self.assertTrue(True)

    def test_intel_exclude_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(exclude={'middle_name'})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])

    def test_intel_exclude_deep_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(exclude={'middle_name': True, 'bag': {'things': True}})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('things', json_schema['$defs']['Bag']['properties'])

    def test_intel_exclude_deeper_json_schema(self):
        PersonCopy = Person.model_inc_ex_class_copy(
            exclude={'middle_name': True, 'bag': {'pockets': True, 'things': {'description': True}}}
        )

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('pockets', json_schema['$defs']['Bag']['properties'])
        self.assertNotIn('description', json_schema['$defs']['Thing']['properties'])

