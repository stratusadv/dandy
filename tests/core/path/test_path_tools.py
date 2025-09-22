from unittest import TestCase

from dandy.core.exceptions import DandyCriticalException
from dandy.core.path.tools import get_file_path_or_exception


class TestPathTools(TestCase):
    def test_get_file_path_or_exception(self):
        with self.assertRaises(DandyCriticalException):
            message = 'this/path/doesnt/exist'
            get_file_path_or_exception(message)
