from pathlib import Path
from typing import Any

from dandy.application.agent.session import session
from dandy.domain.tool.tool import BaseTool
from dandy.shared.cancellation import stop_signal


class RunCommandTool(BaseTool):
    name = 'run_command'
    description = (
        'Run a shell command inside the project directory and return its output. '
        'The command runs without asking for confirmation. '
        'Use this to install dependencies, run tests, run linters, or build the project. '
        'The command can use shell features such as pipes and environment variables.'
    )

    action_label = 'Executing'
    action_ascii_char = '◦'
    can_mutate_state = True

    timeout_seconds = 30
    use_shell = True

    @property
    def working_directory(self) -> Path:
        return session.project_base_path

    def action_output(self, **kwargs: Any) -> str:
        return f'{kwargs["command"]}'

    def handle(self, command: str, timeout_seconds: int = 30) -> str:
        return self.run_subprocess(
            command=command, timeout_seconds=timeout_seconds, stop_signal=stop_signal
        )
