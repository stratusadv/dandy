from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from dandy.core.path.tools import get_file_path_or_exception
from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.file.mixin import FileServiceMixin


class FileService(BaseService['FileServiceMixin']):
    obj: FileServiceMixin

    def append(self, file_path: Path | str, content: str | bytes = ''):
        if self.exists(file_path):
            with open(file_path, 'ab') as f:
                f.write(content)

        else:
            self.write(file_path, content)

    @staticmethod
    def exists(file_path: Path | str) -> bool:
        return Path(file_path).exists()

    @staticmethod
    def make_directory(directory_path: Path | str):
        Path(directory_path).mkdir(parents=True, exist_ok=True)

    def mkdir(self, file_path: Path | str):
        self.make_directory(file_path)

    @staticmethod
    def read(file_path: Path | str) -> str | bytes:
        get_file_path_or_exception(file_path=file_path)

        with open(file_path, 'rb') as f:
            return f.read()

    @staticmethod
    def remove(file_path: Path | str):
        Path(file_path).unlink(missing_ok=True)

    def reset_service(self):
        pass

    def rm(self, file_path: Path | str):
        self.remove(file_path)

    def write(self, file_path: Path | str, content: str | bytes):
        path = Path(file_path)
        # Ensure parent directory exists
        self.make_directory(path.parent)

        with open(path, 'wb') as f:
            f.write(content)

