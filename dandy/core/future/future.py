import concurrent.futures
from concurrent.futures import Future
from time import perf_counter

from typing_extensions import Callable, TypeVar, Generic

from dandy.core.future.exceptions import FutureCriticalException

async_executor = concurrent.futures.ThreadPoolExecutor()

FutureResultType = TypeVar('FutureResultType')


class AsyncFuture(Generic[FutureResultType]):
    def __init__(self, callable_: Callable[..., FutureResultType], *args, **kwargs):
        self._future: Future = async_executor.submit(callable_, *args, **kwargs)
        self._future_start_time = perf_counter()

        self._result = None
        self._result_timeout = None
        self._using_result_timeout = False

    def cancel(self):
        if not self._future.done():
            self._future.cancel()

    @property
    def result(self) -> FutureResultType:
        if self._result:
            return self._result
        
        try:
            done, not_done = concurrent.futures.wait([self._future], timeout=self._result_timeout)
            
            if self._future in done:
                self._result: FutureResultType = self._future.result()

                return self._result
            else:
                raise concurrent.futures.TimeoutError
        except concurrent.futures.TimeoutError:
            raise FutureCriticalException(f'Future timed out after {self._result_timeout} seconds')
        finally:
            del self._future
                
    def set_timeout(self, seconds: int):
        self._using_result_timeout = True
        self._result_timeout = seconds
