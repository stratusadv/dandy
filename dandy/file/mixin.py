from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.file.service import FileService


class FileServiceMixin(BaseServiceMixin):
    _file_service: FileService = ...

    @property
    def file(self) -> FileService:
        if self._file_service is ...:
            self._file_service = FileService(
                obj=self
            )

        return self._file_service

    def reset_services(self):
        super().reset_services()
