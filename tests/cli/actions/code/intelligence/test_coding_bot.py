from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from dandy.cli.actions.code.intelligence.bots.coding_bot import CodingBot
from dandy.cli.session import session
from dandy.http.intelligence.intel import HttpResponseIntel


def tool_call_response(tool_name: str, arguments: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': None,
                        'tool_calls': [
                            {
                                'id': 'call_1',
                                'type': 'function',
                                'function': {
                                    'name': tool_name,
                                    'arguments': arguments,
                                },
                            }
                        ],
                    }
                }
            ]
        }
    )


def content_response(content: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': content,
                    }
                }
            ]
        }
    )


class TestCodingBotToolLoop(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_coding_bot_reads_then_edits_a_file(self, mock_post_request: mock.MagicMock) -> None:
        target_path = Path(self.temp_directory_path, 'sample.txt')
        target_path.write_text('hello world')

        mock_post_request.side_effect = [
            tool_call_response('read_file', '{"file_path": "sample.txt"}'),
            tool_call_response(
                'edit_file',
                '{"file_path": "sample.txt", "old_string": "hello world", '
                '"new_string": "hello dandy"}',
            ),
            content_response('{"text": "Updated sample.txt to greet Dandy."}'),
        ]

        result = CodingBot().process('Update sample.txt to greet Dandy')

        self.assertEqual(result.text, 'Updated sample.txt to greet Dandy.')
        self.assertEqual(target_path.read_text(), 'hello dandy')

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_coding_bot_creates_a_new_file(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            tool_call_response(
                'write_file',
                '{"file_path": "nested/new_file.txt", "content": "brand new file"}',
            ),
            content_response('{"text": "Created nested/new_file.txt."}'),
        ]

        result = CodingBot().process('Create nested/new_file.txt with the text brand new file')

        self.assertEqual(result.text, 'Created nested/new_file.txt.')
        self.assertEqual(
            Path(self.temp_directory_path, 'nested', 'new_file.txt').read_text(),
            'brand new file',
        )
