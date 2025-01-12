import sys
from io import StringIO
from unittest import TestCase, mock
from dandy.cli.main import main

class TestCli(TestCase):
    def setUp(self):
        self.held = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.held

    def test_cli_without_arguments(self):
        test_args = []
        with mock.patch('sys.argv', ['dandy'] + test_args):
            main()

        output = sys.stdout.getvalue().strip()

        self.assertIn("usage: dandy [-h]", output)

    # def test_cli(self):
    #     from dandy.cli.main import main
    #
    #     main()
    #
    #     self.assertTrue(True)
