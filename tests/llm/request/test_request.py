import base64
from pathlib import Path
from unittest import TestCase

from dandy.file.utils import get_file_path_or_exception
from dandy.llm.config import LlmConfig
from dandy.file.image.utils import get_image_mime_type_from_base64_string


class TestRequest(TestCase):
    def test_config_request_body(self):
        request_body = LlmConfig('DEFAULT').generate_request_body()

        with open(get_file_path_or_exception(Path('assets', 'images', 'vision_test_people_and_animal.jpg')),
                  "rb") as img:
            test_image_bytes = base64.b64encode(img.read())
            test_image_string = test_image_bytes.decode('utf-8')

        request_body.messages.add_message(
            role='system',
            text='You are a helpful assistant.',
            image_base64_strings=[
                test_image_string
            ]
        )

        self.assertEqual(
            request_body.messages[0].content[0].type,
            'text'
        )
        self.assertEqual(
            request_body.messages[0].content[0].text,
            'You are a helpful assistant.'
        )

        self.assertEqual(
            request_body.messages[0].content[1].type,
            'image_url'
        )
        self.assertEqual(
            request_body.messages[0].content[1].image_url.url,
            f'data:{get_image_mime_type_from_base64_string(test_image_string)};base64,{test_image_string}'
        )

        request_body_dict = request_body.to_dict()

        self.assertEqual(type(request_body_dict), dict)
