from dandy.cli.intelligence.tools.subprocess_utils import run_subprocess
from dandy.cli.session import session
from dandy.tool.tool import BaseTool


class GitStatusTool(BaseTool):
    name = 'git_status'
    description = (
        'Show the current git working tree status using "git status --short". '
        'Returns one short line per changed, staged, or untracked file.'
    )

    def action_sentence(self) -> str:
        return 'Checking the git working tree status.'

    def handle(self) -> str:
        return run_subprocess(
            command=['git', 'status', '--short'],
            cwd=session.project_base_path,
            timeout_seconds=10,
            use_shell=False,
        )
