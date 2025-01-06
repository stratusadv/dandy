import concurrent.futures
from time import time

from typing_extensions import Callable, TypeVar, Generic, Union

from dandy.future.exceptions import FutureException

ASYNC_EXECUTOR = concurrent.futures.ThreadPoolExecutor()

FutureResultType = TypeVar('FutureResultType')


class AsyncFuture(Generic[FutureResultType]):
    def __init__(self, callable_: Callable[..., FutureResultType], *args, **kwargs):
        self._future = ASYNC_EXECUTOR.submit(callable_, *args, **kwargs)
        self._future_start_time = time()

        self._result: Union[FutureResultType, None] = None
        self._result_timeout = None
        self._using_result_timeout = False

    def cancel(self):
        if not self._future.done():
            self._future.cancel()

    @property
    def result(self) -> FutureResultType:
        if self._result is None:
            try:
                done, not_done = concurrent.futures.wait([self._future], timeout=self._result_timeout)
                if self._future in done:
                    self._result = self._future.result()
                else:
                    raise concurrent.futures.TimeoutError
            except concurrent.futures.TimeoutError:
                raise FutureException(f'Future timed out after {self._result_timeout} seconds')
            finally:
                self._future = None
        return self._result

    def set_timeout(self, seconds: int):
        self._using_result_timeout = True
        self._result_timeout = seconds
