import base64
from pathlib import Path
from unittest import TestCase

from dandy.core.path.tools import get_file_path_or_exception
from dandy.llm.conf import llm_configs
from dandy.llm.utils import get_image_mime_type_from_base64_string


class TestRequest(TestCase):
    def test_ollama_config_request_body(self):
        request_body = llm_configs.FAST.generate_request_body(
            temperature=llm_configs.FAST.options.temperature,
            seed=llm_configs.FAST.options.seed,
        )

        request_body.add_message(
            'system',
            'You are a helpful assistant.'
        )

        self.assertEqual(request_body.messages[0].content, 'You are a helpful assistant.')

    def test_openai_config_request_body(self):
        request_body = llm_configs.GPT_4o_MINI.generate_request_body(
            temperature=llm_configs.GPT_4o_MINI.options.temperature,
            seed=llm_configs.GPT_4o_MINI.options.seed,
        )

        with open(get_file_path_or_exception(Path('assets', 'images', 'vision_test_image.jpg')), "rb") as img:
            test_image_bytes = base64.b64encode(img.read())
            test_image_string = test_image_bytes.decode('utf-8')

        request_body.add_message(
            'system',
            'You are a helpful assistant.',
            [test_image_string]
        )

        self.assertEqual(request_body.messages[0].content[0]['type'],
                         'text')
        self.assertEqual(request_body.messages[0].content[0]['text'],
                         'You are a helpful assistant.')

        self.assertEqual(request_body.messages[0].content[1]['type'], 'image_url')
        self.assertEqual(request_body.messages[0].content[1]['image_url']['url'],
                         f'data:{get_image_mime_type_from_base64_string(test_image_string)};base64,{test_image_string}')

        request_body_dict = request_body.to_dict()

        self.assertEqual(type(request_body_dict),dict)

        request_body.set_format_to_text()
        self.assertEqual(request_body.response_format['type'], 'text')