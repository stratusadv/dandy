from time import perf_counter
from unittest import TestCase
import time

from dandy.core.future.tools import process_to_future


class TestTools(TestCase):
    def test_process_to_future(self):
        run_count = 150
        run_seconds = 0.1

        def sleepy_function(seconds: int) -> int:
            time.sleep(seconds)
            return seconds

        start = perf_counter()

        futures = [
            process_to_future(sleepy_function, seconds=run_seconds)
            for _ in range(run_count)
        ]

        total_seconds = 0.0

        for future in futures:
            total_seconds += future.result

        self.assertAlmostEqual(total_seconds, run_count * run_seconds, 3)
        self.assertEqual(len(futures), run_count)
        self.assertLess(perf_counter() - start, 1.0)
