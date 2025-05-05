import os
from functools import wraps

from dandy.core.exceptions import DandyException


def nines_testing(nines: int = int(os.getenv("TESTING_NINES", 0))):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if nines == 0:
                func(
                    *args,
                    **kwargs
                )

            else:
                print(f'Running {func.__qualname__} {nines} nines testing ...')

                loop_count = 10 ** nines
                has_raised_one_exception = False

                for _ in range(loop_count):
                    try:
                        func(
                            *args,
                            **kwargs
                        )

                    except Exception as e:
                        if isinstance(e, DandyException) and not has_raised_one_exception:
                            has_raised_one_exception = True

                        else:
                            raise e

        return wrapper

    return decorator
