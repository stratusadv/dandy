from dandy.cli.intelligence.tools.paths import _resolve_project_path
from dandy.cli.intelligence.tools.subprocess_utils import run_subprocess
from dandy.cli.session import session
from dandy.tool.tool import BaseTool


class GitDiffTool(BaseTool):
    name = 'git_diff'
    description = (
        'Show uncommitted changes using "git diff". '
        'The path is relative to the project root (empty means the whole repository). '
        'Returns diffs for tracked files that have been modified but not yet staged.'
    )

    def handle(self, path: str = '') -> str:
        try:
            git_args = ['git', 'diff']

            if path:
                relative_path = _resolve_project_path(path).relative_to(
                    session.project_base_path.resolve()
                )
                git_args.extend(['--', str(relative_path)])
        except Exception as error:
            return f'Error running git diff: {error}'

        return run_subprocess(
            command=git_args, cwd=session.project_base_path, timeout_seconds=10, use_shell=False
        )
