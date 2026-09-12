from pathlib import Path
from typing import Any

from dandy.cli.intelligence.tools.paths import resolve_project_path
from dandy.cli.intelligence.tools.tool_errors import tool_error
from dandy.cli.session import session
from dandy.tool.tool import BaseTool


class GitDiffTool(BaseTool):
    name = 'git_diff'
    description = (
        'Show uncommitted changes using "git diff". '
        'The path is relative to the project root (empty means the whole repository). '
        'Returns diffs for tracked files that have been modified but not yet staged.'
    )

    timeout_seconds = 10

    @property
    def working_directory(self) -> Path:
        return session.project_base_path

    def action_sentence(self, **kwargs: Any) -> str:
        path = kwargs.get('path') or ''

        return f'Showing the git diff for {path}.' if path else 'Showing the git diff.'

    @tool_error('running git diff')
    def handle(self, path: str = '') -> str:
        git_args = ['git', 'diff']

        if path:
            relative_path = resolve_project_path(path).relative_to(
                session.project_base_path.resolve()
            )
            git_args.extend(['--', str(relative_path)])

        return self.run_subprocess(command=git_args)
