from dandy.cli.tools.intel import GitDiffIntel, GitStatusIntel
from dandy.cli.tools.paths import _resolve_project_path
from dandy.cli.tools.subprocess_utils import run_subprocess
from dandy.cli.session import session
from dandy.tool.tool import BaseTool


class GitStatusTool(BaseTool):
    name = 'git_status'
    description = (
        'Show the current git working tree status using "git status --short". '
        'Returns one short line per changed, staged, or untracked file.'
    )
    intel_class = GitStatusIntel

    def handle(self, arguments: GitStatusIntel) -> str:  # noqa: ARG002
        return run_subprocess(
            command=['git', 'status', '--short'],
            cwd=session.project_base_path,
            timeout_seconds=10,
            use_shell=False,
        )


class GitDiffTool(BaseTool):
    name = 'git_diff'
    description = (
        'Show uncommitted changes using "git diff". '
        'The path is relative to the project root (empty means the whole repository). '
        'Returns diffs for tracked files that have been modified but not yet staged.'
    )
    intel_class = GitDiffIntel

    def handle(self, arguments: GitDiffIntel) -> str:
        try:
            git_args = ['git', 'diff']

            if arguments.path:
                relative_path = _resolve_project_path(arguments.path).relative_to(
                    session.project_base_path.resolve()
                )
                git_args.extend(['--', str(relative_path)])
        except Exception as error:
            return f'Error running git diff: {error}'

        return run_subprocess(
            command=git_args,
            cwd=session.project_base_path,
            timeout_seconds=10,
            use_shell=False,
        )
