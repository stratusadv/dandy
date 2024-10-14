import concurrent.futures
from time import sleep, time

from typing_extensions import Callable, TypeVar, Generic, Union

from dandy.future.exceptions import FutureException


ASYNC_EXECUTOR_RESULT_CHECK_INTERVAL = 0.001
ASYNC_EXECUTOR = concurrent.futures.ThreadPoolExecutor()

FutureResultType = TypeVar('FutureResultType')


class AsyncExecutorFuture:
    def __init__(self, func: Callable[..., FutureResultType], *args, **kwargs):
        self._future = ASYNC_EXECUTOR.submit(func, *args, **kwargs)
        self._result: Union[FutureResultType, None] = None
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
    def result(self) -> FutureResultType:

        while not self._future.done():
            sleep(ASYNC_EXECUTOR_RESULT_CHECK_INTERVAL)

            self._increment_result_timer()

            if self._has_timed_out:
                raise FutureException(f'Future timed out after {self._result_timeout} seconds')

        try:
            self._result = self._future.result()
            return self._result
        except concurrent.futures.TimeoutError:
            raise FutureException(f'Future timed out')
        finally:
            self._future = None

    def set_timeout(self, seconds: int):
        self._result_timeout = seconds