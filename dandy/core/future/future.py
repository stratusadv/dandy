from __future__ import annotations

import concurrent.futures

from typing import Callable, TypeVar, Generic, TYPE_CHECKING, Any

from dandy.core.future.exceptions import (
    FutureRecoverableException,
    FutureCriticalException,
)

if TYPE_CHECKING:
    from concurrent.futures import Future

async_executor = concurrent.futures.ThreadPoolExecutor()

FutureResultType = TypeVar("FutureResultType")


class AsyncFuture(Generic[FutureResultType]):
    def __init__(self, callable_: Callable[..., FutureResultType], *args, **kwargs):
        self._future: Future = async_executor.submit(callable_, *args, **kwargs)

        self._result: Any = None
        self._result_fetched: bool = False
        self._result_timeout: float | None = None
        self._using_result_timeout: bool = False

    def cancel(self) -> bool:
        return self._future.cancel()

    def cancelled(self) -> bool:
        return self._future.cancelled()

    def done(self) -> bool:
        return self._future.done()

    @property
    def result(self) -> FutureResultType:
        if self._result_fetched:
            return self._result

        try:
            self._result: FutureResultType = self._future.result(
                timeout=self._result_timeout
            )
            self._result_fetched = True

        except concurrent.futures.TimeoutError as error:
            self.cancel()
            message = f"Future timed out after {self._result_timeout} seconds"
            raise FutureRecoverableException(message) from error

        return self._result

    def set_timeout(self, seconds: float):
        if seconds <= 0:
            message = f"Future timeout must be greater than 0.0, not {seconds}"
            raise FutureCriticalException(message)

        self._result_timeout = seconds
