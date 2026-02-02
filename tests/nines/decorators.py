import os
from functools import wraps
from typing import Callable

from dandy.core.exceptions import DandyError


def nines_testing(nines: int = int(os.getenv("TESTING_NINES", '0'))):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            if nines == 0:
                func(
                    *args,
                    **kwargs
                )

            else:
                loop_count = 10 ** nines

                nines_string = str(float('0.' + '9' * nines) * 100)

                print(f'\nRunning "{func.__qualname__}" with Nines Testing at {nines_string}% Pass Rate Requirement ...')

                has_raised_one_exception = False

                for _ in range(loop_count):
                    try:
                        func(
                            *args,
                            **kwargs
                        )

                    except Exception as error:
                        if isinstance(error, DandyError) and not has_raised_one_exception:
                            has_raised_one_exception = True
                        else:
                            raise

        return wrapper

    return decorator
