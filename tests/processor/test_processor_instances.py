from unittest import TestCase

from dandy import Bot, Decoder


class TestProcessorInstances(TestCase):
    def test_processor_instances(self):
        new_bot = Bot()

        new_bot_answer = new_bot.process('In one lower case word tell me what sound do Cats Make?')

        new_decoder = Decoder(
            mapping_keys_description='Cats',
            mapping={
                'one cat': 'meow',
                'two cats': 'meow meow'
            }
        )

        new_decoder_answer = new_decoder.process('I would like to see a single cat.')

        another_bot = Bot()

        another_bot_answer = another_bot.process('In one lower case word tell me what sound do Dogs Make?')

        another_decoder = Decoder(
            mapping_keys_description='Dogs',
            mapping={
                'one dog': 'woof',
                'two dogs': 'woof woof'
            }
        )

        another_decoder_answer = another_decoder.process('I would like to see a pair of dogs.')

        alterative_decoder_answer = another_decoder.process('I would like to see a single of dog.')

        end_decoder_answer = new_decoder.process('I would like to see a two cats.')


        self.assertIn(new_bot_answer.text, 'meow')
        self.assertEqual(new_decoder_answer[0], 'meow')
        self.assertIn(another_bot_answer.text, ('woof', 'bark'))
        self.assertEqual(another_decoder_answer[0], 'woof woof')
        self.assertEqual(alterative_decoder_answer[0], 'woof')
        self.assertEqual(end_decoder_answer[0], 'meow meow')
