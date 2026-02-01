from unittest import TestCase

from dandy import Bot

CATS_KWARGS = {
    'keys_description': 'Cats',
    'keys_values': {
        'one cat': 'meow',
        'two cats': 'meow meow'
    }

}

DOGS_KWARGS = {
    'keys_description': 'Dogs',
    'keys_values': {
        'one dog': 'woof',
        'two dogs': 'woof woof'
    }

}


class TestProcessorInstances(TestCase):
    def test_processor_instances(self):
        new_bot = Bot()

        new_bot_answer = new_bot.llm.prompt_to_intel('In one lower case word tell me what sound do Cats Make?')

        new_decoder = Bot()

        new_decoder_answer = new_decoder.llm.decoder.prompt_to_values(
            prompt='I would like to see a single cat.',
            **CATS_KWARGS
        )

        another_bot = Bot()

        another_bot_answer = another_bot.llm.prompt_to_intel('In one lower case word tell me what sound do Dogs Make?')

        another_decoder = Bot()

        another_decoder_answer = another_decoder.llm.decoder.prompt_to_values(
            prompt='I would like to see a pair of dogs.',
            **DOGS_KWARGS
        )

        alterative_decoder_answer = another_decoder.llm.decoder.prompt_to_values(
            prompt='I would like to see a single of dog.',
            **DOGS_KWARGS
        )

        end_decoder_answer = new_decoder.llm.decoder.prompt_to_values(
            prompt='I would like to see a two cats.',
            **CATS_KWARGS
        )

        self.assertIn(new_bot_answer.text, 'meow')
        self.assertEqual(new_decoder_answer[0], 'meow')
        self.assertIn(another_bot_answer.text, ('woof', 'bark'))
        self.assertEqual(another_decoder_answer[0], 'woof woof')
        self.assertEqual(alterative_decoder_answer[0], 'woof')
        self.assertEqual(end_decoder_answer[0], 'meow meow')
