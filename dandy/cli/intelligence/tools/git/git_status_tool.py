from pathlib import Path

from dandy.cli.session import session
from dandy.tool.tool import BaseTool


class GitStatusTool(BaseTool):
    name = 'git_status'
    description = (
        'Show the current git working tree status using "git status --short". '
        'Returns one short line per changed, staged, or untracked file.'
    )

    timeout_seconds = 10

    @property
    def working_directory(self) -> Path:
        return session.project_base_path

    def action_sentence(self) -> str:
        return 'Checking the git working tree status.'

    def handle(self) -> str:
        return self.run_subprocess(command=['git', 'status', '--short'])
