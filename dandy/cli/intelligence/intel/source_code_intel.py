from pathlib import Path
from typing import Literal

from dandy import BaseIntel
from dandy.file.utils import write_to_file


class SourceCodeIntel(BaseIntel):
    recommended_file_name: str
    language: Literal['python']
    extension: Literal['py']
    code: str

    def write_to_directory(self, dir_path: Path | str):
        write_to_file(
            file_path=Path(dir_path) / self.recommended_file_name,
            content=self.code,
        )
