import base64
import os
from unittest import TestCase

from dandy.conf import settings
from dandy.core.exceptions import DandyCriticalException
from dandy.core.utils import json_default, encode_file_to_base64, python_obj_to_markdown
from dandy.intel.intel import BaseIntel


class TestCoreUtils(TestCase):
    def test_json_default_serializer(self):
        serialized_object = json_default(
            CampFireIntel(
                logs=9,
                temperature=1078.9
            )
        )

        self.assertEqual(serialized_object['temperature'], 1078.9)

    def test_encode_file_to_base64(self):
        with self.assertRaises(DandyCriticalException):
            encode_file_to_base64('this/path/doesnt/exist')

        fname = os.path.join(settings.BASE_PATH , 'assets', 'images', 'vision_test_image.jpg')

        with open(fname, 'rb') as f:
            self.assertEqual(
                encode_file_to_base64(fname),
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

class CampFireIntel(BaseIntel):
    logs: int
    temperature: float
