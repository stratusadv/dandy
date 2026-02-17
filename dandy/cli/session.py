from pathlib import Path

from dandy import BaseIntel
from dandy.conf import settings
from dandy.constants import CLI_WORKING_DIRECTORY
from dandy.file.utils import file_exists


class DandyCliSession(BaseIntel):
    project_base_path: Path | None = None
    cli_working_directory: Path | None = None
    is_loaded: bool = False

    def post_init(self, project_base_path: Path) -> None:
        self.project_base_path = project_base_path
        self.cli_working_directory = Path(
            self.project_base_path,
            settings.DANDY_DIRECTORY,
            CLI_WORKING_DIRECTORY,
        )

    @property
    def session_file_path(self) -> Path:
        return Path(self.cli_working_directory, 'session.json')

    def load(self):
        if file_exists(self.session_file_path):
            loaded_session = DandyCliSession.create_from_file(self.session_file_path)

            loaded_session.project_base_path = self.project_base_path
            loaded_session.cli_working_directory = self.cli_working_directory

            self.__dict__.update(loaded_session.__dict__)

            self.is_loaded = True

    def save(self):
        self.save_to_file(self.session_file_path)
        self.is_loaded = True


session = DandyCliSession()
