from typing import Callable, TypeVar

from dandy.core.future.future import AsyncFuture

R = TypeVar('R')


def process_to_future(
        callable_: Callable[..., R],
        *args,
        **kwargs
) -> AsyncFuture[R]:
    return AsyncFuture[R](callable_, *args, **kwargs)
