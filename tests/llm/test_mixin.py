from unittest import TestCase

from tests.bot.intelligence.bots import TestingBot, OtherBot
from tests.bot.intelligence.intel import HappyIntel, SadIntel


class TestLlmMixin(TestCase):
    def test_processor_with_mixin(self):
        testing_bot = TestingBot()

        self.assertEqual(testing_bot.role, "Parrot Assistant")

        testing_bot.role = "Not Testing Master"

        self.assertEqual(testing_bot.role, "Not Testing Master")

        another_bot = TestingBot(task="Do another thing")

        self.assertEqual(another_bot.task, "Do another thing")

        happy_intel = testing_bot.process(
            "I wear country hats",
        )

        self.assertIsInstance(happy_intel, HappyIntel)

    def test_multiple_processor_with_mixin(self):
        testing_bot = TestingBot()
        other_bot = OtherBot()

        self.assertEqual(testing_bot.role, "Parrot Assistant")
        self.assertEqual(other_bot.role, "Cockatiel Assistant")

        happy_intel = testing_bot.process(
            "I wear sombreros",
        )

        sad_intel = other_bot.process(
            "I wear a black and white makeup",
        )

        self.assertIsInstance(happy_intel, HappyIntel)
        self.assertIsInstance(sad_intel, SadIntel)


