from pathlib import Path

from dandy import Prompt
from dandy.bot.bot import Bot
from dandy.cli.session import session
from dandy.file.utils import get_directory_listing


class FilesDecoderBot(Bot):
    def process(self, prompt: Prompt | str):
        return self.llm.decoder.prompt_to_values(
            prompt=prompt,
            keys_description='Project Files',
            keys_values={
                **{file_path: file_path
                   for file_path in get_directory_listing(
                        dir_path=Path(session.project_base_path),
                        max_depth=None,
                        file_extensions=['py', 'md'],
                    )
                   },
            }
        )
