import unittest
from unittest import TestCase

from dandy.conf import settings


class TestSimpleExample(TestCase):
    def test_settings_loaded(self):
        self.assertIsNotNone(settings)
        self.assertTrue(hasattr(settings, 'LLM_CONFIGS'))
        self.assertIn('DEFAULT', settings.LLM_CONFIGS)


if __name__ == '__main__':
    unittest.main()
