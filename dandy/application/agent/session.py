from pathlib import Path

from dandy.shared.constants import CLI_WORKING_DIRECTORY, DANDY_LOCAL_DIRECTORY_NAME
from dandy.domain.intel.intel import BaseIntel


class DandyCliSession(BaseIntel):
    project_base_path: Path

    def post_init(self, project_base_path: Path) -> None:
        self.project_base_path = project_base_path

    @property
    def project_dandy_path(self) -> Path:
        return Path(self.project_base_path, DANDY_LOCAL_DIRECTORY_NAME)

    @property
    def project_dandy_cli_path(self) -> Path:
        return Path(self.project_dandy_path, CLI_WORKING_DIRECTORY)


session = DandyCliSession(project_base_path=Path.cwd())
