import os
from functools import wraps

from dandy.core.exceptions import DandyException


def nines_testing(nines: int = int(os.getenv("TESTING_NINES", 0))):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if nines == 0:
                func(
                    *args,
                    **kwargs
                )

            else:
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
                            print(f'{func.__qualname__} {nines} nines testing ... Failed')
                            raise e

                print(f'{func.__qualname__} {nines} nines testing ... Passed')


        return wrapper

    return decorator
