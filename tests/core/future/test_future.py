from time import perf_counter, sleep
from unittest import TestCase
from itertools import combinations

from dandy.processor.bot.bot import Bot
from dandy.core.future import AsyncFuture
from dandy.core.future.exceptions import FutureRecoverableException
from dandy.intel.intel import BaseIntel
from tests.processor.bot.intelligence.bots import TestingBot, OtherBot


class StoryIntel(BaseIntel):
    text: str


class PirateStoryBot(Bot):
    def process(self, message):
        return self.llm.prompt_to_intel(
            prompt=message,
            intel_class=StoryIntel,
        )


TEST_FUTURE_SLEEP_TIME = 5.0
TEST_FUTURE_PROCESS_TIME = TEST_FUTURE_SLEEP_TIME + (TEST_FUTURE_SLEEP_TIME * 0.1)


def square_number(x: int) -> int:
    sleep(TEST_FUTURE_SLEEP_TIME)
    return x * x


class TestFuture(TestCase):
    def setUp(self):
        self.start_time = perf_counter()

    def test_future(self):
        squared_future = AsyncFuture(square_number, 5)
        another_squared_future = AsyncFuture(square_number, 10)

        sleep(TEST_FUTURE_SLEEP_TIME)

        self.assertTrue(squared_future.result == 25)
        self.assertTrue(another_squared_future.result == 100)

        self.assertTrue(perf_counter() - self.start_time <= TEST_FUTURE_PROCESS_TIME)

    def test_future_timeout(self):
        with self.assertRaises(FutureRecoverableException):
            squared_future = AsyncFuture(square_number, 5)
            squared_future.set_timeout(0.1)
            _ = squared_future.result

    def test_bot_future(self):
        response_future = PirateStoryBot().process_to_future(
            'Write a quick poem about pirates enjoying a day at the beach.',
        )

        self.assertTrue(len(response_future.result.text) > 0)

    def test_bot_race_condition_future(self):
        testing_bot = TestingBot()
        other_bot = OtherBot()
        testy_bot = TestingBot()
        othering_bot = OtherBot()

        bot_prompts = [
            (testing_bot, 'fedora hats and canes'),
            (other_bot, 'I wear a bowler hat and enjoy fighting'),
            (testy_bot, 'Ball gowns and Chandeliers'),
            (othering_bot, 'I wear a soldier helmet and I came back from WW2'),
            (testing_bot, 'With a clown wig and balloons'),
            (other_bot, 'Steam top Hat and a Monocle'),
            (testy_bot, 'Wet boot on my head and I am missing teeth'),
            (othering_bot, 'Spiked hair and some army boots'),
            (testing_bot, 'I caught fire and now Fireworks are my Hat'),
            (other_bot, 'Graduation cap because I am graduating today'),
            (testy_bot, 'Using my shirt as a hat and my belt as shoes'),
            (othering_bot, 'I am the hat now ... the univers wears me'),
        ]

        futures = [bot.process_to_future(prompt) for bot, prompt in bot_prompts]

        results = [future.result for future in futures]

        for result1, result2 in combinations(results, 2):
            self.assertNotEqual(
                result1.sentence,
                result2.sentence,
                f"Descriptions should not match: {result1.sentence} == {result2.sentence}"
            )

    def test_future_cancel(self):
        squared_future = AsyncFuture(square_number, 5)
        self.assertNotEqual(squared_future.cancel(), squared_future._future.running())
