from unittest import TestCase

from dandy.llm import Prompt
from dandy.llm.utils import get_estimated_token_count_for_prompt, get_image_mime_type_from_base64_string


class TestLlmUtils(TestCase):
    def test_get_estimated_token_count_for_prompt(self):
        token_count = get_estimated_token_count_for_prompt(
            prompt=(
                Prompt()
                .text('Hello World')
            )
        )

        self.assertGreater(token_count, 0)

    def test_get_image_mime_type_from_base64_string(self):
        self.assertEqual(get_image_mime_type_from_base64_string('JVBERi0'), 'application/pdf')
        self.assertEqual(get_image_mime_type_from_base64_string('R0lGODdh'), 'image/gif')
        self.assertEqual(get_image_mime_type_from_base64_string('R0lGODlh'), 'image/gif')
        self.assertEqual(get_image_mime_type_from_base64_string('iVBORw0KGgo'), 'image/png')
        self.assertEqual(get_image_mime_type_from_base64_string('/9j/'), 'image/jpg')
        self.assertEqual(get_image_mime_type_from_base64_string('random nonsense'), None)