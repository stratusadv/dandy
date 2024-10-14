from time import time, sleep
from unittest import TestCase

from dandy.future.executor import AsyncExecutorFuture

class TestFuture(TestCase):
    def test_future(self):
        def my_function(x):
            import time
            time.sleep(1)
            return x * x  # Function to compute square of input

        start_time = time()

        future = AsyncExecutorFuture(my_function, 5)

        print("Doing some other tasks...")
        sleep(0.3)

        print("Doing some more tasks...")
        sleep(0.3)

        end_time = time()

        print(f"Function completed and returned: {future.result}")

        execution_time = end_time - start_time

        print(f"Execution time: {execution_time:.2f} seconds")

        self.assertTrue(execution_time <= 1.2)