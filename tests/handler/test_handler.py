from unittest import TestCase


class TestHandler(TestCase):
    def test_handler_import(self):
        from dandy.handler.handler import Handler
        self.assertTrue(type(Handler) is type(Handler))