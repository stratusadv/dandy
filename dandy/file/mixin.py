from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.file.service import FileService


class FileServiceMixin(BaseServiceMixin):
    file_config: str = 'DEFAULT'

    file: ClassVar[FileService] = FileService()
    _FileService_instance: FileService | None = None

    def reset_services(self):
        super().reset_services()
