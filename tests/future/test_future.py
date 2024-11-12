from time import time, sleep
from unittest import TestCase

from dandy.future.future import AsyncFuture
from example.pirate.crew.datasets import CREW_MEMBERS
from example.pirate.crew.intelligence.bots.crew_selection_llm_bot import CrewSelectionLlmBot


TEST_FUTURE_SLEEP_TIME = 2.0
TEST_FUTURE_PROCESS_TIME = TEST_FUTURE_SLEEP_TIME + 0.05


class TestFuture(TestCase):
    def setUp(self):
        self.start_time = time()

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

        self.assertTrue(time() - self.start_time <= TEST_FUTURE_PROCESS_TIME)

    def test_llmbot_future(self):
        crew_choices_future = CrewSelectionLlmBot.process_to_future(
            'I would like a random selection of exactly one captain, one navigator, and one engineer.',
            CREW_MEMBERS
        )

        engineer_choices_future = CrewSelectionLlmBot.process_to_future(
            'I would like a random selection of exactly one engineer.',
            CREW_MEMBERS
        )

        sleep(TEST_FUTURE_SLEEP_TIME)

        _ = engineer_choices_future.result

        self.assertTrue(len(crew_choices_future.result) == 3)

        self.assertTrue(time() - self.start_time <= TEST_FUTURE_PROCESS_TIME)
