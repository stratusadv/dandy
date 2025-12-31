from pathlib import Path

from dandy import Bot
from dandy.conf import settings
from tests.vision.intelligence.intel import ImageIntel


class PeopleCountingBot(Bot):
    llm_config = 'VISION'
    llm_role = 'People Counter'
    llm_task = 'Count people in an image.'
    llm_intel_class = ImageIntel

    def process(self, image_file: Path) -> ImageIntel:
        return self.vision.image_prompt_to_intel(
            prompt=f'Count people in this image',
            image_file_paths=[
                image_file
            ],
        )