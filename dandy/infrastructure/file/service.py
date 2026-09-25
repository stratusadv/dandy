from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.shared.service.service import BaseService
from dandy.shared import files

if TYPE_CHECKING:
    from pathlib import Path


class FileService(BaseService['dandy.infrastructure.file.mixin.FileServiceMixin']):

    @staticmethod
    def append(file_path: Path | str, content: str):
        files.append_to_file(file_path, content)

    @staticmethod
    def exists(file_path: Path | str) -> bool:
        return files.file_exists(file_path)

    @staticmethod
    def make_directory(directory_path: Path | str):
        files.make_directory(directory_path)

    def mkdir(self, file_path: Path | str):
        self.make_directory(file_path)

    @staticmethod
    def read(file_path: Path | str) -> str:
        return files.read_from_file(file_path)

    @staticmethod
    def remove(file_path: Path | str):
        files.remove_file(file_path)

    @staticmethod
    def remove_directory(directory_path: Path | str):
        files.remove_directory(directory_path)

    def reset(self):
        pass

    def rm(self, file_path: Path | str):
        self.remove(file_path)

    @staticmethod
    def write(file_path: Path | str, content: str):
        files.write_to_file(file_path, content)

