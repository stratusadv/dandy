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
        with self.assertRaises(IntelCriticalException):
            _ = Person.model_inc_ex_class_copy(include={'height'})

    def test_intel_include_with_required_field(self):
        with self.assertRaises(IntelCriticalException):
            _ = Person.model_inc_ex_class_copy(include={'middle_name'})

    def test_intel_exclude_with_required_field(self):
        with self.assertRaises(IntelCriticalException):
            _ = Person.model_inc_ex_class_copy(exclude={'first_name'})

    def test_intel_include_and_exclude(self):
        with self.assertRaises(IntelCriticalException):
            _ = Person.model_inc_ex_class_copy(include={'middle_name'}, exclude={'first_name'})

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

    def test_intel_model_validate_and_copy(self):
        old_bag = Bag(
            color='blue',
            stylish=True
        )

        new_bag = old_bag.model_validate_and_copy(
            {"things": [{"name": "keys"}, {"name": "wallet"}]}
        )

        if new_bag.things is not None:
            self.assertIsInstance(new_bag.things[0], Thing)
        else:
            self.assertFalse(True)

    def test_intel_model_validate_json_and_copy(self):
        old_bag = Bag(color="blue", stylish=True)

        new_bag = old_bag.model_validate_json_and_copy(
            '{"things": [{"name": "keys"}, {"name": "wallet"}]}'
        )

        if new_bag.things is not None:
            self.assertIsInstance(new_bag.things[0], Thing)
        else:
            self.assertFalse(True)

    def test_intel_object_exclude_required_filled_field(self):
        try:
            bag = Bag(color="blue", stylish=True)

            _ = bag.model_inc_ex_class_copy(exclude={'stylish'}, intel_object=bag)

            self.assertTrue(True)
        except IntelCriticalException:
            self.assertFalse(True)

    def test_intel_object_include_required_empty_field(self):
        with self.assertRaises(IntelCriticalException):
            bag = Bag(color="blue", stylish=True)

            bag.stylish = None

            _ = bag.model_inc_ex_class_copy(include={'color', 'pockets'}, intel_object=bag)
