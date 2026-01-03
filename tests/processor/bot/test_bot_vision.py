from pathlib import Path
from typing import List, Type
from unittest import TestCase

from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from dandy.llm.options.options import LlmOptions
from dandy.llm.prompt.prompt import Prompt


class PersonIntel(BaseIntel):
    hat: bool
    description: str


class ImageBreakdownIntel(BaseIntel):
    description: str
    buildings: int
    elk: int
    fire_hydrants: int
    vehicles: int
    lamp_posts: int
    people: list[PersonIntel]


class ImageBreakdownLlmBot(Bot):
    config = 'GEMMA_3_12B_VISION'
    config_options = LlmOptions(
        temperature=0.1,
    )

    def process(
            self,
            prompt: Prompt,
            intel_class: Type[ImageBreakdownIntel],
            image_files: List[str | Path],
    ) -> ImageBreakdownIntel:
        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
            image_files=image_files,
        )


class TestLlmBotVision(TestCase):
    pass
    # @run_llm_configs(['GEMMA_3_12B_VISION', 'GPT_4o'])
    # def test_llm_bot_intel_class_include(self, llm_config: str):
    #     ImageBreakdownLlmBot.config = llm_config
    #
    #     image_breakdown_intel = ImageBreakdownLlmBot.process(
    #         prompt=(
    #             Prompt()
    #             .text('Please describe the following image and count the objects in the image?')
    #             .text('Count all the vehicles even if they are partially visible.')
    #             .text('How many buildings are there in the image?')
    #             .text('Respond with a description for each person in the image.')
    #         ),
    #         intel_class=ImageBreakdownIntel,
    #         image_files=[
    #             Path(settings.BASE_PATH, 'assets', 'images', 'vision_test_image.jpg'),
    #         ],
    #     )
    #
    #     self.assertEqual(image_breakdown_intel.elk, 1)
    #     self.assertEqual(image_breakdown_intel.buildings, 2)
