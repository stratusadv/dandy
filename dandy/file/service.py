from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService
from dandy.file import utils

if TYPE_CHECKING:
    from pathlib import Path


class FileService(BaseService['dandy.file.mixin.FileServiceMixin']):

    @staticmethod
    def append(file_path: Path | str, content: str):
        utils.append_to_file(file_path, content)

    @staticmethod
    def exists(file_path: Path | str) -> bool:
        return utils.file_exists(file_path)

    @staticmethod
    def make_directory(directory_path: Path | str):
        utils.make_directory(directory_path)

    def mkdir(self, file_path: Path | str):
        self.make_directory(file_path)

    @staticmethod
    def read(file_path: Path | str) -> str:
        return utils.read_from_file(file_path)

    @staticmethod
    def remove(file_path: Path | str):
        utils.remove_file(file_path)

    @staticmethod
    def remove_directory(directory_path: Path | str):
        utils.remove_directory(directory_path)

    def reset_service(self):
        pass

    def rm(self, file_path: Path | str):
        self.remove(file_path)

    @staticmethod
    def write(file_path: Path | str, content: str):
        utils.write_to_file(file_path, content)
