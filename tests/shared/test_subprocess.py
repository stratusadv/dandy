import sys
from pathlib import Path
from unittest import TestCase

from dandy.shared.subprocess import run_subprocess

CWD = Path.cwd()


class TestRunSubprocess(TestCase):
    def run_python(self, code: str, timeout_seconds: int = 10) -> str:
        return run_subprocess(
            [sys.executable, '-c', code], cwd=CWD, timeout_seconds=timeout_seconds
        )

    def test_stdout_only(self) -> None:
        output = self.run_python('print("hello stdout")')

        self.assertEqual(output, 'Exit code: 0\nhello stdout\n')

    def test_stderr_only(self) -> None:
        output = self.run_python('import sys; sys.stderr.write("hello stderr")')

        self.assertEqual(output, 'Exit code: 0\nSTDERR:\nhello stderr')

    def test_stdout_and_stderr(self) -> None:
        output = self.run_python('import sys; print("out"); sys.stderr.write("err")')

        self.assertEqual(output, 'Exit code: 0\nSTDOUT:\nout\n\nSTDERR:\nerr')

    def test_non_zero_exit_code_is_reported(self) -> None:
        output = self.run_python('import sys; sys.exit(3)')

        self.assertTrue(output.startswith('Exit code: 3\n'))

    def test_timeout_returns_error_message(self) -> None:
        output = self.run_python('import time; time.sleep(30)', timeout_seconds=1)

        self.assertEqual(output, 'Error: command timed out after 1 seconds.')

    def test_os_error_returns_error_message(self) -> None:
        command = ['/nonexistent/binary/that/does/not/exist']
        output = run_subprocess(command, cwd=CWD, timeout_seconds=10)

        self.assertTrue(output.startswith('Error: failed to run command:'))

    def test_output_is_truncated_at_character_limit(self) -> None:
        output = self.run_python('print("a" * 9000)')

        self.assertTrue(output.startswith('Exit code: 0\n'))
        self.assertTrue(output.endswith('\n... (truncated)'))
        body = output[len('Exit code: 0\n') :]
        self.assertLessEqual(len(body), 8000 + len('\n... (truncated)'))
