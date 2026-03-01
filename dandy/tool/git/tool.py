import subprocess
from pathlib import Path

from dandy.tool.tool import BaseTool


class GitTool(BaseTool):
    def setup(self) -> bool:
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                check=True
            )

            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def diff_file(self, file_path: Path | str) -> dict:
        file_path_str = str(file_path)

        try:
            result = subprocess.run(
                ['git', 'diff', file_path_str],
                capture_output=True,
                text=True,
                check=True
            )

            return {
                'file_path': file_path_str,
                'diff': result.stdout,
                'has_changes': bool(result.stdout.strip()),
                'error': None
            }

        except subprocess.CalledProcessError as e:
            return {
                'error': f'Git command failed: {e.stderr}',
                'file_path': file_path_str,
                'diff': None
            }

        except Exception as e:
            return {
                'error': f'Unexpected error: {str(e)}',
                'file_path': file_path_str,
                'diff': None
            }
