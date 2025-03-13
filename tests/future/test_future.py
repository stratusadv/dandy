from time import perf_counter, sleep
from unittest import TestCase

from dandy.core.future import AsyncFuture

from dandy.llm import LlmBot

TEST_FUTURE_SLEEP_TIME = 5.0
TEST_FUTURE_PROCESS_TIME = TEST_FUTURE_SLEEP_TIME + (TEST_FUTURE_SLEEP_TIME * 0.1)


class TestFuture(TestCase):
    def setUp(self):
        self.start_time = perf_counter()

    def test_future(self):
        def square_number(x) -> int:
            import time
            time.sleep(TEST_FUTURE_SLEEP_TIME)
            return x * x

        squared_future= AsyncFuture(square_number, 5)
        another_squared_future = AsyncFuture(square_number, 10)

        sleep(TEST_FUTURE_SLEEP_TIME)

        self.assertTrue(squared_future.result == 25)
        self.assertTrue(another_squared_future.result == 100)

        self.assertTrue(perf_counter() - self.start_time <= TEST_FUTURE_PROCESS_TIME)

    def test_llmbot_future(self):
        response_future = LlmBot.process_to_future(
            'Write a quick poem about pirates enjoying a day at the beach.',
        )

        self.assertTrue(len(response_future.result.text) > 0)
