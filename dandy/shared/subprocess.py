import subprocess
from pathlib import Path

_COMMAND_OUTPUT_CHARACTER_LIMIT = 8000


def run_subprocess(
    command: list[str] | str, cwd: Path, timeout_seconds: int, use_shell: bool = False
) -> str:
    """Run a command and return its output, never raising.

    Output is capped to `_COMMAND_OUTPUT_CHARACTER_LIMIT` characters and
    combined stdout/stderr are prefixed with an exit-code line.
    """

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=use_shell,
            check=False,
        )

    except subprocess.TimeoutExpired:
        return f'Error: command timed out after {timeout_seconds} seconds.'

    except OSError as error:
        return f'Error: failed to run command: {error}'

    output = completed.stdout or ''
    error_output = completed.stderr or ''

    if output and error_output:
        combined = f'STDOUT:\n{output}\nSTDERR:\n{error_output}'
    elif error_output:
        combined = f'STDERR:\n{error_output}'
    else:
        combined = output

    if len(combined) > _COMMAND_OUTPUT_CHARACTER_LIMIT:
        combined = combined[:_COMMAND_OUTPUT_CHARACTER_LIMIT] + '\n... (truncated)'

    return f'Exit code: {completed.returncode}\n{combined}'
