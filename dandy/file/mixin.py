from dandy.core.service.mixin import BaseServiceMixin
from dandy.file.service import FileService


class FileServiceMixin(BaseServiceMixin):
    @property
    def file(self) -> FileService:
        return self._get_service_instance(FileService)

    def reset(self):
        super().reset()
        self.file.reset()
