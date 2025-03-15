from pathlib import Path
from unittest import TestCase

from pydantic.main import IncEx
from typing_extensions import Union, List, Type

from dandy.conf import settings
from dandy.debug import DebugRecorder
from dandy.intel import BaseIntel
from dandy.llm import BaseLlmBot, Prompt
from dandy.core.processor.processor import BaseProcessor


class ImageBreakdown(BaseIntel):
    description: str
    humans: int
    wild_animals: int


class ImageBreakdownLlmBot(BaseLlmBot[ImageBreakdown]):
    config = 'GEMMA_3_12B_VISION'

    @classmethod
    def process(
            cls,
            user_input: str,
            intel_class: Type[ImageBreakdown],
            image_files: List[str | Path],
    ) -> ImageBreakdown:
        return cls.process_prompt_to_intel(
            prompt=Prompt(user_input),
            intel_class=intel_class,
            image_files=image_files,
        )


class TestLlmBotVision(TestCase):
    def test_llm_bot_intel_class_include(self):
        DebugRecorder.start_recording('test_llm_vision')

        image_breakdown = ImageBreakdownLlmBot.process(
            user_input='Please describe the following image and tell me how many humans and wild animals are in it?',
            intel_class=ImageBreakdown,
            image_files=[Path(settings.BASE_PATH, 'assets', 'images', 'vision_test_image.jpg')],
        )

        DebugRecorder.stop_recording('test_llm_vision')

        DebugRecorder.to_html_file('test_llm_vision')

        print(image_breakdown)

        self.assertTrue(True)
