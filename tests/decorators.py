import os
from functools import wraps

from dandy.core.exceptions import DandyException


def nines_testing(nines: int = int(os.getenv("TESTING_NINES", 0))):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if nines == 0:
                func(
                    self,
                    *args,
                    **kwargs
                )

            else:
                loop_count = int(10 * nines)
                raised_one_exception = False

                for _ in range(loop_count):
                    try:
                        func(
                            self,
                            *args,
                            **kwargs
                        )

                        print(f'{func.__qualname__} {nines} nines testing ... Passed')

                    except Exception as e:
                        if isinstance(e, DandyException):
                            if raised_one_exception:
                                print(f'{func.__qualname__} {nines} nines testing ... Failed')
                                raise e

                            raised_one_exception = True

                        else:
                            print(f'{func.__qualname__} {nines} nines testing ... Failed')
                            raise e

        return wrapper

    return decorator
