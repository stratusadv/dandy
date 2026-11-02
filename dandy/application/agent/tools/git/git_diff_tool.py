from pathlib import Path
from typing import Any

from dandy.application.agent.tools.paths import resolve_project_path
from dandy.application.agent.tools.tool_errors import tool_error
from dandy.application.agent.session import session
from dandy.domain.tool.tool import BaseTool


class GitDiffTool(BaseTool):
    name = 'git_diff'
    description = (
        'Show uncommitted changes using "git diff". '
        'The path is relative to the project root (empty means the whole repository). '
        'Returns diffs for tracked files that have been modified but not yet staged.'
    )

    action_label = 'Showing git diff'

    timeout_seconds = 10

    @property
    def working_directory(self) -> Path:
        return session.project_base_path

    def action_output(self, **kwargs: Any) -> str | None:
        path = kwargs.get('path') or ''

        return f'for {path}' if path else None

    @tool_error('running git diff')
    def handle(self, path: str = '') -> str:
        git_args = ['git', 'diff']

        if path:
            relative_path = resolve_project_path(path).relative_to(
                session.project_base_path.resolve()
            )
            git_args.extend(['--', str(relative_path)])

        return self.run_subprocess(command=git_args)
