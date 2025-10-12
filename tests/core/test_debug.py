from unittest import TestCase
from dandy.core.debug import dandy_warning_handler


class TestDebug(TestCase):
    def test_dandy_warning_handler(self):
        test_message = "Test warning message"
        dandy_warning_handler(
            message=test_message,
            category=UserWarning,
            filename="test.py",
            lineno=1,
            file=None,
            line=None,
        )
