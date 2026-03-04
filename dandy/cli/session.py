from pathlib import Path

from dandy import BaseIntel
from dandy.conf import settings
from dandy.constants import CLI_WORKING_DIRECTORY
from dandy.file.utils import file_exists


class DandyCliSession(BaseIntel):
    project_base_path: Path
    is_loaded: bool = False

    def post_init(self, project_base_path: Path) -> None:
        self.project_base_path = project_base_path

    @property
    def project_dandy_path(self) -> Path:
        return Path(
            self.project_base_path,
            settings.DANDY_DIRECTORY,
        )

    @property
    def project_dandy_cli_path(self) -> Path:
        return Path(
            self.project_dandy_path,
            CLI_WORKING_DIRECTORY,
        )


    @property
    def session_file_path(self) -> Path:
        return Path(self.project_dandy_cli_path, 'session.json')

    def load(self) -> None:
        if file_exists(self.session_file_path):
            loaded_session = DandyCliSession.create_from_file(self.session_file_path)

            loaded_session.project_base_path = self.project_base_path

            self.__dict__.update(loaded_session.__dict__)

            self.is_loaded = True

    def save(self) -> None:
        self.save_to_file(self.session_file_path)
        self.is_loaded = True


session = DandyCliSession(
    project_base_path=Path.cwd()
)
