from unittest import TestCase

from tests.processor.bot.intelligence.bots import TestingBot, OtherBot
from tests.processor.bot.intelligence.intel import HappyIntel, SadIntel


class TestLlmMixin(TestCase):
    def test_processor_with_mixin(self):
        testing_bot = TestingBot()

        self.assertEqual(testing_bot.llm_role, "Master of Art Descriptions")

        testing_bot.llm_role = "Not Testing Master"

        self.assertEqual(testing_bot.llm_role, "Not Testing Master")

        another_bot = TestingBot(llm_task="Do another thing")

        self.assertEqual(another_bot.llm_task, "Do another thing")

        happy_intel = testing_bot.process(
            "I wear country hats",
        )

        self.assertIsInstance(happy_intel, HappyIntel)

    def test_multiple_processor_with_mixin(self):
        testing_bot = TestingBot()
        other_bot = OtherBot()

        self.assertEqual(testing_bot.llm_role, "Master of Art Descriptions")
        self.assertEqual(other_bot.llm_role, "Potato Dish Designer")

        happy_intel = testing_bot.process(
            "I wear sombreros",
        )

        sad_intel = other_bot.process(
            "I wear a black and white makeup",
        )

        self.assertIsInstance(happy_intel, HappyIntel)
        self.assertIsInstance(sad_intel, SadIntel)


