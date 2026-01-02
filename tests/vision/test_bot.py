from pathlib import Path
from unittest import TestCase

from dandy.conf import settings
from tests.vision.intelligence.bots.people_counting_bot import PeopleCountingBot
from tests.vision.intelligence.intel import ImageCompareIntel

INVALID_SETTINGS_MODULE_NAME = 'tests.invalid_dandy_settings'


class TestVisionBot(TestCase):
    def test_vision_bot(self):
        people_counting_bot = PeopleCountingBot()

        image_intel = people_counting_bot.process(
            Path(settings.BASE_PATH, 'assets', 'images', 'vision_test_people_and_animal.jpg')
        )

        print(image_intel.people_count)

        self.assertGreater(image_intel.people_count, 2)

    def test_vision_compare(self):
        bot = PeopleCountingBot()

        image_compare_intel = bot.vision.image_prompt_to_intel(
            prompt=f'What is in this two pictures and what is the difference?',
            intel_class=ImageCompareIntel,
            image_file_paths=[
                Path(settings.BASE_PATH, 'assets', 'images', 'vision_test_compare_all_objects.jpg'),
                Path(settings.BASE_PATH, 'assets', 'images', 'vision_test_compare_some_objects.jpg')
            ],
        )

        print(image_compare_intel)


