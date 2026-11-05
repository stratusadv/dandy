from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.shared.service.service import BaseService
from dandy.shared import files

if TYPE_CHECKING:
    from pathlib import Path


class FileService(BaseService['dandy.infrastructure.file.mixin.FileServiceMixin']):
    @staticmethod
    def append(file_path: Path | str, content: str) -> None:
        files.append_to_file(file_path, content)

    @staticmethod
    def exists(file_path: Path | str) -> bool:
        return files.file_exists(file_path)

    @staticmethod
    def make_directory(directory_path: Path | str) -> None:
        files.make_directory(directory_path)

    def mkdir(self, file_path: Path | str) -> None:
        self.make_directory(file_path)

    @staticmethod
    def read(file_path: Path | str) -> str:
        return files.read_from_file(file_path)

    @staticmethod
    def remove(file_path: Path | str) -> None:
        files.remove_file(file_path)

    @staticmethod
    def remove_directory(directory_path: Path | str) -> None:
        files.remove_directory(directory_path)

    def reset(self) -> None:
        pass

    def rm(self, file_path: Path | str) -> None:
        self.remove(file_path)

    @staticmethod
    def write(file_path: Path | str, content: str) -> None:
        files.write_to_file(file_path, content)
