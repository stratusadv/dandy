from unittest import TestCase

from dandy.shared.exceptions import DandyCriticalError
from dandy.shared.files import get_file_path_or_exception


class TestPathTools(TestCase):
    def test_get_file_path_or_exception(self):
        with self.assertRaises(DandyCriticalError):
            message = 'this/path/doesnt/exist'
            get_file_path_or_exception(message)
