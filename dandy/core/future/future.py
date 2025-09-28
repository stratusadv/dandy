from __future__ import annotations

import concurrent.futures
from time import perf_counter

from typing import Callable, TypeVar, Generic, TYPE_CHECKING

from dandy.core.future.exceptions import FutureRecoverableException

if TYPE_CHECKING:
    from concurrent.futures import Future

async_executor = concurrent.futures.ThreadPoolExecutor()

FutureResultType = TypeVar('FutureResultType')


class AsyncFuture(Generic[FutureResultType]):
    def __init__(self, callable_: Callable[..., FutureResultType], *args, **kwargs):
        self._future: Future = async_executor.submit(callable_, *args, **kwargs)
        self._future_start_time = perf_counter()

        self._result = None
        self._result_timeout = None
        self._using_result_timeout = False

    def cancel(self) -> bool:
        return self._future.cancel()

    @property
    def result(self) -> FutureResultType:
        if self._result:
            return self._result

        try:
            done, not_done = concurrent.futures.wait(
                [self._future],
                timeout=self._result_timeout
            )

            if self._future in done:
                self._result: FutureResultType = self._future.result()

                return self._result
            raise concurrent.futures.TimeoutError
        except concurrent.futures.TimeoutError:
            message = f'Future timed out after {self._result_timeout} seconds'
            raise FutureRecoverableException(message)
        finally:
            del self._future

    def set_timeout(self, seconds: int):
        self._using_result_timeout = True
        self._result_timeout = seconds
