import concurrent.futures
from time import sleep, time

from typing_extensions import Callable

from dandy.future.exceptions import FutureException

ASYNC_EXECUTOR_RESULT_CHECK_INTERVAL = 0.001


class AsyncExecutorFuture:
    def __init__(self, func: Callable, *args, **kwargs):
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.future = self.executor.submit(func, *args, **kwargs)
        self._result = None
        self._result_timeout = 0.0
        self._result_timer = 0.0

    def _increment_result_timer(self):
        if self._has_timeout:
            self._result_timer += ASYNC_EXECUTOR_RESULT_CHECK_INTERVAL

    @property
    def _has_timed_out(self):
        if self._has_timeout:
            return self._result_timer >= self._result_timeout

    @property
    def _has_timeout(self):
        return self._result_timeout > 0.0

    @property
    def result(self):

        while not self.future.done():
            sleep(ASYNC_EXECUTOR_RESULT_CHECK_INTERVAL)

            self._increment_result_timer()

            if self._has_timed_out:
                raise FutureException(f'Future timed out after {self._result_timeout} seconds')

        try:
            self._result = self.future.result()
            return self._result
        except concurrent.futures.TimeoutError as e:
            raise FutureException(f'Future timed out: {e}')
        except Exception as e:
            raise FutureException(f'A problem occurred during async execution: {e}')
        finally:
            del self.future

    def set_timeout(self, seconds: int):
        self._result_timeout = seconds