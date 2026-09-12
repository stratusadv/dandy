from pathlib import Path
from typing import Any

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

    timeout_seconds = 30
    use_shell = True

    @property
    def working_directory(self) -> Path:
        return session.project_base_path

    def action_sentence(self, **kwargs: Any) -> str:
        return f'Running "{kwargs["command"]}".'

    def handle(self, command: str, timeout_seconds: int = 30) -> str:
        return self.run_subprocess(command=command, timeout_seconds=timeout_seconds)
