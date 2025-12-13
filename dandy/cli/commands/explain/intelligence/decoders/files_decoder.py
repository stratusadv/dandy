from pathlib import Path

from dandy import Decoder
from dandy.cli.conf import config
from dandy.core.path.tools import get_directory_listing


class FilesDecoder(Decoder):
    mapping_keys_description = 'Project Files'
    mapping = {
        **{file_path: file_path
           for file_path in get_directory_listing(
                dir_path=Path(config.project_base_path / 'dandy'),
                max_depth=None,
                file_extensions=['py', 'md'],
            )
           },
        **{
            file_path: file_path
            for file_path in get_directory_listing(
                dir_path=Path(config.project_base_path / 'docs'),
                max_depth=None,
                file_extensions=['py', 'md'],
            )
        },
        **{
            file_path: file_path
            for file_path in get_directory_listing(
                dir_path=Path(config.project_base_path / 'example'),
                max_depth=None,
                file_extensions=['py', 'md'],
            )
        },
        **{
            file_path: file_path
            for file_path in get_directory_listing(
                dir_path=Path(config.project_base_path / 'tests'),
                max_depth=None,
                file_extensions=['py', 'md'],
            )
        }
    }
