from time import perf_counter, sleep
from unittest import TestCase

from dandy.processor.bot.bot import Bot
from dandy.core.future import AsyncFuture
from dandy.core.future.exceptions import FutureRecoverableException
from dandy.intel.intel import BaseIntel
from tests.bot.intelligence.bots import TestingBot, OtherBot


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


def square_number(x) -> int:
    import time
    time.sleep(TEST_FUTURE_SLEEP_TIME)
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
            squared_future.set_timeout(1)
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

        happy_intel_future = testing_bot.process_to_future(
            'fedora hats and canes'
        )

        sad_intel_future = other_bot.process_to_future(
            'I wear a bowler hat and enjoy fighting'
        )

        more_happy_intel_future = testy_bot.process_to_future(
            'Ball gowns and Chandelers'
        )

        more_sad_intel_future = othering_bot.process_to_future(
            'I wear a soldier helmet and I came back from WW2'
        )

        _1 = testing_bot.process_to_future(
            'With a clown wig and balloons'
        )

        _2 = testing_bot.process_to_future(
            'Steam top Hat and a Monocle'
        )

        _3 = testing_bot.process_to_future(
            'Wet boot on my head and I am missing teeth'
        )

        _4 = testing_bot.process_to_future(
            'Spiked hair and some army boots'
        )

        happy_intel = happy_intel_future.result
        sad_intel = sad_intel_future.result
        more_happy_intel = more_happy_intel_future.result
        more_sad_intel = more_sad_intel_future.result

        _ = _1.result
        _ = _2.result
        _ = _3.result
        _ = _4.result

        # print(f'{happy_intel=}')
        # print(f'{sad_intel=}')
        # print(f'{more_happy_intel=}')
        # print(f'{more_sad_intel=}')

        self.assertNotEqual(happy_intel.description, sad_intel.description)
        self.assertNotEqual(happy_intel.description, more_sad_intel.description)
        self.assertNotEqual(happy_intel.description, more_happy_intel.description)
        self.assertNotEqual(more_happy_intel.description, sad_intel.description)
        self.assertNotEqual(more_happy_intel.description, more_sad_intel.description)

    def test_future_cancel(self):
        squared_future = AsyncFuture(square_number, 5)
        self.assertNotEqual(squared_future.cancel(), squared_future._future.running())
