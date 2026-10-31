from unittest import TestCase

from dandy import Bot
from tests.consts import live_llm_test

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


@live_llm_test
class TestProcessorInstances(TestCase):
    def test_processor_instances(self):
        new_bot = Bot()

        new_bot_answer = new_bot.llm.prompt_to_intel('In one lower case word tell me what sound do Cats Make?')

        new_bot = Bot()

        new_bot_decision = new_bot.llm.decision.prompt_to_values(
            prompt='I would like to see a single cat.',
            **CATS_KWARGS
        )

        another_bot = Bot()

        another_bot_answer = another_bot.llm.prompt_to_intel('In one lower case word tell me what sound do Dogs Make?')

        another_bot = Bot()

        another_bot_decision = another_bot.llm.decision.prompt_to_values(
            prompt='I would like to see a pair of dogs.',
            **DOGS_KWARGS
        )

        alterative_bot_decision = another_bot.llm.decision.prompt_to_values(
            prompt='I would like to see a single of dog.',
            **DOGS_KWARGS
        )

        end_bot_decision = new_bot.llm.decision.prompt_to_values(
            prompt='I would like to see a two cats.',
            **CATS_KWARGS
        )

        self.assertIn(new_bot_answer.text, 'meow')
        self.assertEqual(new_bot_decision[0], 'meow')
        self.assertIn(another_bot_answer.text, ('woof', 'bark'))
        self.assertEqual(another_bot_decision[0], 'woof woof')
        self.assertEqual(alterative_bot_decision[0], 'woof')
        self.assertEqual(end_bot_decision[0], 'meow meow')
