from typing import Any

from dandy.cli.intelligence.tools.subprocess_utils import run_subprocess
from dandy.cli.session import session
from dandy.tool.tool import BaseTool


class RunCommandTool(BaseTool):
    name = 'run_command'
    description = (
        'Run a shell command inside the project directory and return its output. '
        'The command runs without asking for confirmation. '
        'Use this to install dependencies, run tests, run linters, or build the project. '
        'The command can use shell features such as pipes and environment variables.'
    )

    def action_sentence(self, **kwargs: Any) -> str:
        return f'Running "{kwargs["command"]}".'

    def handle(self, command: str, timeout_seconds: int = 30) -> str:
        return run_subprocess(
            command=command,
            cwd=session.project_base_path,
            timeout_seconds=timeout_seconds,
            use_shell=True,
        )
