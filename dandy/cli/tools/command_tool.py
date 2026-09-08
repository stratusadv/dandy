from dandy.cli.tools.intel import RunCommandIntel
from dandy.cli.tools.subprocess_utils import run_subprocess
from dandy.cli.session import session
from dandy.cli.tui.tui import tui
from dandy.tool.tool import BaseTool


class RunCommandTool(BaseTool):
    name = 'run_command'
    description = (
        'Run a shell command inside the project directory and return its output. '
        'Every command must be approved by the user before it executes. '
        'Use this to install dependencies, run tests, run linters, or build the project. '
        'The command can use shell features such as pipes and environment variables.'
    )
    intel_class = RunCommandIntel

    def handle(self, arguments: RunCommandIntel) -> str:
        response = tui.get_user_input(question=f'Run command "{arguments.command}"?')

        if response is None or str(response).lower().strip() not in {'y', 'yes'}:
            return 'Command was not approved.'

        return run_subprocess(
            command=arguments.command,
            cwd=session.project_base_path,
            timeout_seconds=arguments.timeout_seconds,
            use_shell=True,
        )
