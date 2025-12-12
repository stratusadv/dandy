from pathlib import Path

from dandy import Decoder
from dandy.conf import settings
from dandy.core.path.tools import get_directory_listing


class FilesDecoder(Decoder):
    mapping_keys_description = 'Project Files'
    mapping = {
        file_path: file_path
        for file_path in get_directory_listing(
            dir_path=Path(settings.BASE_PATH / 'dandy'),
            max_depth=None,
        )
    }