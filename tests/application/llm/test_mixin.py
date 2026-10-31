from unittest import TestCase

from tests.application.bot.intelligence.bots import ParrotBot, OtherBot
from tests.application.bot.intelligence.intel import HappyIntel, SadIntel
from tests.consts import live_llm_test


@live_llm_test
class TestLlmMixin(TestCase):
    def test_processor_with_mixin(self):
        parrot_bot = ParrotBot()

        self.assertEqual(parrot_bot.role, "Parrot Assistant")

        parrot_bot.role = "Not Testing Master"

        self.assertEqual(parrot_bot.role, "Not Testing Master")

        another_bot = ParrotBot(task="Do another thing")

        self.assertEqual(another_bot.task, "Do another thing")

        happy_intel = parrot_bot.process(
            "I wear country hats",
        )

        self.assertIsInstance(happy_intel, HappyIntel)

    def test_multiple_processor_with_mixin(self):
        parrot_bot = ParrotBot()
        other_bot = OtherBot()

        self.assertEqual(parrot_bot.role, "Parrot Assistant")
        self.assertEqual(other_bot.role, "Cockatiel Assistant")

        happy_intel = parrot_bot.process(
            "I wear sombreros",
        )

        sad_intel = other_bot.process(
            "I wear a black and white makeup",
        )

        self.assertIsInstance(happy_intel, HappyIntel)
        self.assertIsInstance(sad_intel, SadIntel)


