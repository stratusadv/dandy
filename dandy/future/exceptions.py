from dandy.core.exceptions import DandyException


class FutureException(DandyException):
    pass


def raise_future_timeout_exception(timeout):
    raise FutureException(f'Future timed out after {timeout} seconds')