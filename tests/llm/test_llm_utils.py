from unittest import TestCase

from dandy.file.image.utils import get_image_mime_type_from_base64_string


class TestLlmUtils(TestCase):
    def test_get_image_mime_type_from_base64_string(self):
        self.assertEqual(get_image_mime_type_from_base64_string('JVBERi0'), 'application/pdf')
        self.assertEqual(get_image_mime_type_from_base64_string('R0lGODdh'), 'image/gif')
        self.assertEqual(get_image_mime_type_from_base64_string('R0lGODlh'), 'image/gif')
        self.assertEqual(get_image_mime_type_from_base64_string('iVBORw0KGgo'), 'image/png')
        self.assertEqual(get_image_mime_type_from_base64_string('/9j/'), 'image/jpg')
        self.assertEqual(get_image_mime_type_from_base64_string('random nonsense'), None)