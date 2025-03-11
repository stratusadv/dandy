from unittest import TestCase

from dandy.core.utils import json_default
from dandy.intel import BaseIntel


class CampFireIntel(BaseIntel):
    logs: int
    temperature: float


class TestUtils(TestCase):
    def test_json_default_serializer(self):
        serialized_object = json_default(
            CampFireIntel(
                logs=9,
                temperature=1078.9
            )
        )

        self.assertEqual(serialized_object['temperature'], 1078.9)