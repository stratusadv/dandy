from dandy.intel.intel import BaseIntel


class ListDirectoryIntel(BaseIntel):
    path: str = ''
    recursive: bool = False


class ReadFileIntel(BaseIntel):
    file_path: str
    start_line: int | None = None
    end_line: int | None = None


class WriteFileIntel(BaseIntel):
    file_path: str
    content: str


class EditFileIntel(BaseIntel):
    file_path: str
    old_string: str
    new_string: str
    replace_all: bool = False


class DeleteFileIntel(BaseIntel):
    file_path: str


class CreateDirectoryIntel(BaseIntel):
    directory_path: str
