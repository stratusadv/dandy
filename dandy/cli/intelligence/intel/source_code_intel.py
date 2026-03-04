from pathlib import Path
from typing import Literal

from dandy import BaseIntel
from dandy.file.utils import write_to_file


class SourceCodeIntel(BaseIntel):
    file_name_with_extension: str
    language: Literal['python']
    code: str

    def write_to_directory(self, dir_path: Path | str) -> None:
        write_to_file(
            file_path=Path(dir_path) / self.file_name_with_extension,
            content=self.code,
        )
