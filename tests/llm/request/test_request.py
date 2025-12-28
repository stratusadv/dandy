import base64
from pathlib import Path
from unittest import TestCase

from dandy.core.path.tools import get_file_path_or_exception
from dandy.llm.conf import LlmConfigs
from dandy.llm.utils import get_image_mime_type_from_base64_string


class TestRequest(TestCase):
    def test_config_request_body(self):
        request_body = LlmConfigs().DEFAULT.generate_request_body(
            temperature=LlmConfigs().DEFAULT.options.temperature,
            seed=LlmConfigs().DEFAULT.options.seed,
        )

        with open(get_file_path_or_exception(Path('assets', 'images', 'vision_test_image.jpg')), "rb") as img:
            test_image_bytes = base64.b64encode(img.read())
            test_image_string = test_image_bytes.decode('utf-8')

        request_body.messages.create_message(
            role='system',
            text='You are a helpful assistant.',
            image_base64_strings=[test_image_string]
        )

        self.assertEqual(
            request_body.messages[0].content.type,
            'text'
        )
        self.assertEqual(
            request_body.messages[0].content.text,
            'You are a helpful assistant.'
        )

        self.assertEqual(
            request_body.messages[0].content.type,
            'image_url'
        )
        self.assertEqual(
            request_body.messages[0].content.image_url.url,
            f'data:{get_image_mime_type_from_base64_string(test_image_string)};base64,{test_image_string}'
        )

        request_body_dict = request_body.to_dict()

        self.assertEqual(type(request_body_dict), dict)
