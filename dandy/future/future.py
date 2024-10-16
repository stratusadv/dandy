import concurrent.futures
from time import sleep, time

from typing_extensions import Callable, TypeVar, Generic, Union

from dandy.future.exceptions import FutureException

ASYNC_EXECUTOR_RESULT_CHECK_INTERVAL = 0.001
ASYNC_EXECUTOR = concurrent.futures.ThreadPoolExecutor()

FutureResultType = TypeVar('FutureResultType')


class AsyncFuture(Generic[FutureResultType]):
    def __init__(self, callable_: Callable[..., FutureResultType], *args, **kwargs):
        self._future = ASYNC_EXECUTOR.submit(callable_, *args, **kwargs)
        self._future_start_time = time()

        self._result: Union[FutureResultType, None] = None
        self._result_timeout = 0.0
        self._using_result_timeout = False

    def _check_result_timeout(self):
        if self._using_result_timeout:
            if self._result_timeout >= (time() - self._future_start_time):
                raise FutureException(f'Future timed out after {self._result_timeout} seconds')

    def _fetch_result(self):
        if self._result is None:
            while not self._future.done():
                sleep(ASYNC_EXECUTOR_RESULT_CHECK_INTERVAL)
                self._check_result_timeout()

            try:
                self._result: FutureResultType = self._future.result()
            except concurrent.futures.TimeoutError:
                raise FutureException(f'Future timed out')
            finally:
                self._future = None

    @property
    def result(self) -> FutureResultType:
        self._fetch_result()

        return self._result

    def set_timeout(self, seconds: int):
        self._using_result_timeout = True
        self._result_timeout = seconds
