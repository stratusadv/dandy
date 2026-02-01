from unittest import TestCase, mock

from faker import Faker

from dandy import Recorder
from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.bot.bot import Bot
from dandy.llm.decoder.exceptions import (
    DecoderCriticalError,
    DecoderRecoverableError,
)
from tests.decorators import nines_testing
from tests.llm.decoder.intelligence.decoders import (
    FunDecoderBot,
)


class TestDecoder(TestCase):
    def test_invalid_decoder(self):
        with self.assertRaises(DecoderCriticalError):
            _ = Bot().llm.decoder.prompt_to_values(
                prompt='I would like to see a single cat.',
                keys_description='Numbers to a String',
                keys_values={
                    123: 'this decoder mapping value is invalid as it needs string keys'
                }
            )

    def test_decoder(self):
        values = FunDecoderBot().process(
            'I enjoy seeing my dog every day and think animals are really cool. Give me two choices of things to do!',
            2
        )

        self.assertEqual(2, len(values))
        self.assertIn(391, values)
        self.assertIn(782, values)

    @nines_testing()
    def test_big_user_decoder(self):
        fake = Faker()

        pk = 976

        user_dictionary = {}

        for _ in range(fake.random_int(min=100, max=500)):
            pk += fake.random_int(min=5, max=50)
            user_dictionary[f'{fake.unique.name()}'] = pk

        name = fake.random_element(user_dictionary.keys())

        Recorder.start_recording('test_big_user_decoder')

        values = Bot().llm.decoder.prompt_to_values(
            prompt=f'I am looking for {name}',
            keys_description= 'Employee First and Last Names',
            keys_values=user_dictionary
        )

        Recorder.stop_recording('test_big_user_decoder')
        Recorder.to_html_file('test_big_user_decoder')

        self.assertEqual(
            name,
            {val: key for key, val in user_dictionary.items()}[values[0]]
        )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_no_keys_decoder_retry(self, mock_post_request: mock.MagicMock):
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

        with self.assertRaises(DecoderRecoverableError):
            value = FunDecoderBot().process(
                'I really like my pet dog and hope to get another one',
                2
            )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_to_many_keys_decoder_retry(self, mock_post_request: mock.MagicMock):
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

        with self.assertRaises(DecoderRecoverableError):
            value = FunDecoderBot().process(
                'I really like my pet dog and hope to get another one',
                2
            )
