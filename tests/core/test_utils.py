import base64
from pathlib import Path
from unittest import TestCase

from dandy.conf import settings
from dandy.core.exceptions import DandyCriticalException
from dandy.core.utils import encode_file_to_base64, python_obj_to_markdown


class TestCoreUtils(TestCase):
    def test_encode_file_to_base64(self):
        with self.assertRaises(DandyCriticalException):
            encode_file_to_base64('this/path/doesnt/exist')

        file_path = Path(settings.BASE_PATH , 'assets', 'images', 'vision_test_people_and_animal.jpg')

        with open(file_path, 'rb') as f:
            self.assertEqual(
                encode_file_to_base64(file_path),
                base64.b64encode(f.read()).decode('utf-8'))

    def test_python_obj_to_markdown_level_gt_6(self):
        python_obj = {
            'a': 1,
            'b': 2
        }

        md = python_obj_to_markdown(python_obj, level=7)

        self.assertEqual(md, '**a**\n\n1\n\n**b**\n\n2\n\n')

    def test_python_obj_to_markdown_list(self):
        python_list = [
            'a',
            'b',
            'c',
            'd'
        ]

        md = python_obj_to_markdown(python_list)

        self.assertEqual(md, '\n\n'.join(python_list) + '\n\n')
