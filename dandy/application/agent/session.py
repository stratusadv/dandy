from pathlib import Path

from dandy.shared.constants import AGENTS_MD_FILE_NAME, DANDY_LOCAL_DIRECTORY_NAME
from dandy.domain.intel.intel import BaseIntel


class DandyCliSession(BaseIntel):
    project_base_path: Path

    @property
    def project_dandy_path(self) -> Path:
        return Path(self.project_base_path, DANDY_LOCAL_DIRECTORY_NAME)

    @property
    def agents_md_path(self) -> Path:
        return Path(self.project_base_path, AGENTS_MD_FILE_NAME)


session = DandyCliSession(project_base_path=Path.cwd())
