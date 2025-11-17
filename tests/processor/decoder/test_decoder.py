from unittest import TestCase, mock

from faker import Faker

from dandy import recorder, Recorder
from dandy.conf import settings
from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.processor.decoder.decoder import Decoder
from dandy.processor.decoder.exceptions import (
    DecoderCriticalException,
    DecoderRecoverableException,
)
from dandy.processor.processor import BaseProcessor
from tests.decorators import nines_testing
from tests.processor.decoder.intelligence.decoders import FunDecoder, DragonDecoder, AdventureGameDecoder, NestedBirdDecoder


class TestDecoder(TestCase):
    def test_decoder_import(self):
        self.assertTrue(type(Decoder) is type(BaseProcessor))

    def test_invalid_decoder(self):
        with self.assertRaises(DecoderCriticalException):
            _ = Decoder(
                mapping_keys_description='Numbers to a String',
                mapping={
                    123: 'this decoder mapping value is invalid as it needs string keys'
                }
            )

    def test_decoder(self):
        values = FunDecoder().process(
            'I enjoy seeing my dog every day and think animals are really cool. Give me two choices of things to do!',
            2
        )

        self.assertEqual(2, len(values))
        self.assertIn(391, values)
        self.assertIn(782, values)

    def test_seperated_nested_decoder(self):
        values = AdventureGameDecoder().process(
            'The player goes left, and is carrying only a bucket on the adventure.',
            1
        )

        self.assertEqual(1, len(values))
        self.assertEqual(DragonDecoder.mapping['The player is packing other stuff'], values[0])

    def test_combined_nested_decoder(self):
        values = NestedBirdDecoder().process(
            'I am a black bird from the famous edgar allen poe poem',
            1
        )

        self.assertEqual(1, len(values))
        self.assertEqual(NestedBirdDecoder.mapping['the bird is dark colored']['it is a raven'], values[0])

    @nines_testing()
    def test_big_user_decoder(self):
        fake = Faker()

        pk = 976

        user_dictionary = {}

        for _ in range(fake.random_int(min=100, max=500)):
            pk += fake.random_int(min=5, max=50)
            user_dictionary[f'{fake.unique.name()}'] = pk

        class UserLlmDecoder(Decoder):
            mapping_keys_description = 'Employee First and Last Names'
            mapping = user_dictionary

        name = fake.random_element(user_dictionary.keys())

        Recorder.start_recording('test_big_user_decoder')

        values = UserLlmDecoder().process(
            f'I am looking for {name}',
        )

        Recorder.stop_recording('test_big_user_decoder')
        Recorder.to_html_file('test_big_user_decoder')

        self.assertEqual(
            name,
            {val: key for key, val in user_dictionary.items()}[values[0]]
        )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_no_keys_decoder_retry(self, mock_post_request: mock.MagicMock):
        if settings.LLM_CONFIGS['DEFAULT']['TYPE'] == 'ollama':
            mock_post_request.return_value = HttpResponseIntel(
                status_code=200,
                json_data={
                    'message': {
                        'content': '{"keys": []}',
                    }
                },
            )
        if settings.LLM_CONFIGS['DEFAULT']['TYPE'] == 'openai':
            mock_post_request.return_value = HttpResponseIntel(
                status_code=200,
                json_data={
                    'choices': [
                        {
                            'message': {
                                'content': '{"keys": []}',
                            }
                        }
                    ]
                },
            )

        with self.assertRaises(DecoderRecoverableException):
            value = FunDecoder().process(
                'I really like my pet dog and hope to get another one',
                2
            )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_to_many_keys_decoder_retry(self, mock_post_request: mock.MagicMock):
        if settings.LLM_CONFIGS['DEFAULT']['TYPE'] == 'ollama':
            mock_post_request.return_value = HttpResponseIntel(
                status_code=200,
                json_data={
                    'message': {
                        'content': '{"keys": ["1", "2", "3", "4"]}',
                    }
                },
            )
        if settings.LLM_CONFIGS['DEFAULT']['TYPE'] == 'openai':
            mock_post_request.return_value = HttpResponseIntel(
                status_code=200,
                json_data={
                    'choices': [
                        {
                            'message': {
                                'content': '{"keys": ["1", "2", "3", "4"]}',
                            }
                        }
                    ]
                },
            )

        with self.assertRaises(DecoderRecoverableException):
            value = FunDecoder().process(
                'I really like my pet dog and hope to get another one',
                2
            )
