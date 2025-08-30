from unittest import TestCase

from dandy.intel.intel import BaseIntel
from dandy.intel.exceptions import IntelCriticalException
from tests.intel.intel import ThingIntel, BagIntel, PersonIntel


class TestBaseIntel(TestCase):
    def test_base_intel(self):
        class TestingIntel(BaseIntel):
            pass

        intel = TestingIntel()
        self.assertIsInstance(intel, TestingIntel)

    def test_base_intel_include_invalid_field(self):
        with self.assertRaises(IntelCriticalException):
            _ = PersonIntel.model_inc_ex_class_copy(include={'height'})

    def test_base_intel_include_with_required_field(self):
        with self.assertRaises(IntelCriticalException):
            _ = PersonIntel.model_inc_ex_class_copy(include={'middle_name'})

    def test_base_intel_exclude_with_required_field(self):
        with self.assertRaises(IntelCriticalException):
            _ = PersonIntel.model_inc_ex_class_copy(exclude={'first_name'})

    def test_base_intel_include_and_exclude(self):
        with self.assertRaises(IntelCriticalException):
            _ = PersonIntel.model_inc_ex_class_copy(include={'middle_name'}, exclude={'first_name'})

    def test_base_intel_include_json_schema(self):
        PersonCopy = PersonIntel.model_inc_ex_class_copy(include={'first_name', 'last_name'})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])

    def test_base_intel_include_deep_json_schema(self):
        PersonCopy = PersonIntel.model_inc_ex_class_copy(
            include={'first_name': True, 'last_name': True, 'bag': {'color': True, 'stylish': True}}
        )

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('things', json_schema['$defs']['BagIntel']['properties'])

    def test_base_intel_include_deeper_json_schema(self):
        PersonCopy = PersonIntel.model_inc_ex_class_copy(
            include={'first_name': True, 'last_name': True, 'bag': {'color': True, 'stylish': True, 'things': {'name': True}}}
        )

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('pockets', json_schema['$defs']['BagIntel']['properties'])
        self.assertNotIn('description', json_schema['$defs']['ThingIntel']['properties'])

    def test_base_intel_exclude_invalid_field(self):
        try:
            _ = PersonIntel.model_inc_ex_class_copy(exclude={'height'})

        except IntelCriticalException:
            self.assertTrue(True)

    def test_base_intel_exclude_json_schema(self):
        PersonCopy = PersonIntel.model_inc_ex_class_copy(exclude={'middle_name'})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])

    def test_base_intel_exclude_deep_json_schema(self):
        PersonCopy = PersonIntel.model_inc_ex_class_copy(exclude={'middle_name': True, 'bag': {'things': True}})

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('things', json_schema['$defs']['BagIntel']['properties'])

    def test_base_intel_exclude_deeper_json_schema(self):
        PersonCopy = PersonIntel.model_inc_ex_class_copy(
            exclude={'middle_name': True, 'bag': {'pockets': True, 'things': {'description': True}}}
        )

        json_schema = PersonCopy.model_json_schema()

        self.assertNotIn('middle_name', json_schema['properties'])
        self.assertNotIn('pockets', json_schema['$defs']['BagIntel']['properties'])
        self.assertNotIn('description', json_schema['$defs']['ThingIntel']['properties'])

    def test_base_intel_model_validate_and_copy(self):
        old_bag = BagIntel(
            color='blue',
            stylish=True
        )

        new_bag = old_bag.model_validate_and_copy(
            {"things": [{"name": "keys"}, {"name": "wallet"}]}
        )

        if new_bag.things is not None:
            self.assertIsInstance(new_bag.things[0], ThingIntel)
        else:
            self.assertFalse(True)

    def test_base_intel_model_validate_json_and_copy(self):
        old_bag = BagIntel(color="blue", stylish=True)

        new_bag = old_bag.model_validate_json_and_copy(
            '{"things": [{"name": "keys"}, {"name": "wallet"}]}'
        )

        if new_bag.things is not None:
            self.assertIsInstance(new_bag.things[0], ThingIntel)
        else:
            self.assertFalse(True)

    def test_base_intel_object_exclude_required_filled_field(self):
        try:
            bag = BagIntel(color="blue", stylish=True)

            _ = bag.model_inc_ex_class_copy(exclude={'stylish'}, intel_object=bag)

            self.assertTrue(True)
        except IntelCriticalException:
            self.assertFalse(True)

    def test_base_intel_object_include_required_empty_field(self):
        with self.assertRaises(IntelCriticalException):
            bag = BagIntel(color="blue", stylish=True)

            bag.stylish = None

            _ = bag.model_inc_ex_class_copy(include={'color', 'pockets'}, intel_object=bag)
