from unittest import TestCase

from dandy import Bot, Prompt


class TestLlmMixin(TestCase):
    def test_processor_with_mixin(self):
        class TestingBot(Bot):
            llm_role = 'Master of Testing'
            llm_task = 'Do the best testing you can'
            llm_guidelines = (
                Prompt()
                .list([
                    'Test',
                    'Test some more',
                    'Dance a Little More'
                ])
            )

        test_bot = TestingBot()

        self.assertEqual(test_bot.llm_role, 'Master of Testing')

        test_bot.llm_role = 'Not Testing Master'

        self.assertEqual(test_bot.llm_role, 'Not Testing Master')

        another_bot = TestingBot(
            llm_task = 'Do another thing'
        )

        self.assertEqual(another_bot.llm_task, 'Do another thing')
