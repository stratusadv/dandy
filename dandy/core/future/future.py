from __future__ import annotations

import atexit
import concurrent.futures
import threading

from typing import Callable, TypeVar, Generic, TYPE_CHECKING

from dandy.conf import settings
from dandy.core.future.exceptions import (
    FutureRecoverableException,
    FutureCriticalException,
)

if TYPE_CHECKING:
    from concurrent.futures import Future

thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=settings.FUTURES_MAX_WORKERS,
)

atexit.register(thread_pool_executor.shutdown, wait=True)

R = TypeVar("R")


class AsyncFuture(Generic[R]):
    def __init__(self, callable_: Callable[..., R], *args, **kwargs):
        self._future: Future = thread_pool_executor.submit(callable_, *args, **kwargs)

        self._result: R = None
        self._result_fetched: bool = False
        self._result_timeout: float | None = None
        self._lock = threading.RLock()

    def cancel(self) -> bool:
        return self._future.cancel()

    def cancelled(self) -> bool:
        return self._future.cancelled()

    def done(self) -> bool:
        return self._future.done()

    def get_result(self, timeout_seconds: float | None = None) -> R:
        with self._lock:
            if self._result_fetched:
                return self._result

            try:
                self.set_timeout(timeout_seconds)

                self._result: R = self._future.result(timeout=self._result_timeout)
                self._result_fetched = True

            except concurrent.futures.TimeoutError as error:
                self.cancel()
                message = f"Future timed out after {self._result_timeout} seconds"
                raise FutureRecoverableException(message) from error

            return self._result

    @property
    def result(self) -> R:
        return self.get_result(self._result_timeout)

    def set_timeout(self, seconds: float | None = None):
        if seconds is not None and seconds <= 0:
            message = f"Future timeout must be greater than 0.0, not {seconds}"
            raise FutureCriticalException(message)

        self._result_timeout = seconds
