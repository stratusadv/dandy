from unittest import TestCase

from dandy.intel.intel import BaseListIntel
from tests.intel.intelligence.intel import ThingIntel, ThingsIntel


class TestBaseIntel(TestCase):
    def test_base_list_intel(self):
        class TestingListIntel(BaseListIntel):
            items: list[ThingIntel]

        list_intel = TestingListIntel(items=[
            ThingIntel(name='keys'),
            ThingIntel(name='wallet'),
        ])

        self.assertIsInstance(list_intel, TestingListIntel)

    def test_base_list_intel_len(self):
        things_intel = ThingsIntel(items=[
            ThingIntel(name='keys'),
            ThingIntel(name='wallet'),
            ThingIntel(name='phone'),
        ])

        things_intel.append(ThingIntel(name='hat'))

        self.assertEqual(len(things_intel), 4)