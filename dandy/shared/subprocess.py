import subprocess
import time
from pathlib import Path

from dandy.shared.cancellation import StopSignal
from dandy.shared.utils import truncate_output

_POLL_INTERVAL_SECONDS = 0.1


def run_subprocess(
    command: list[str] | str,
    cwd: Path,
    timeout_seconds: int,
    use_shell: bool = False,
    stop_signal: StopSignal | None = None,
) -> str:
    """Run a command and return its output, never raising.

    Output is capped to `OUTPUT_CHARACTER_LIMIT` characters and
    combined stdout/stderr are prefixed with an exit-code line. When a
    `stop_signal` is given, the command is polled instead of blocked on: if
    the signal is set while it runs, the process is killed and a short error
    line is returned so the caller can notice the stop promptly.
    """

    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=use_shell,
        )

    except OSError as error:
        return f'Error: failed to run command: {error}'

    deadline = time.monotonic() + timeout_seconds

    while True:
        if stop_signal is not None and stop_signal.is_set():
            process.kill()
            process.wait()
            return 'Error: command stopped by user.'

        try:
            stdout, stderr = process.communicate(timeout=_POLL_INTERVAL_SECONDS)
            break

        except subprocess.TimeoutExpired:
            if time.monotonic() >= deadline:
                process.kill()
                process.wait()
                return f'Error: command timed out after {timeout_seconds} seconds.'

    output = stdout or ''
    error_output = stderr or ''

    if output and error_output:
        combined = f'STDOUT:\n{output}\nSTDERR:\n{error_output}'
    elif error_output:
        combined = f'STDERR:\n{error_output}'
    else:
        combined = output

    combined = truncate_output(combined)

    return f'Exit code: {process.returncode}\n{combined}'
