from pathlib import Path
from unittest import TestCase

from dandy.conf import settings
from tests.vision.intelligence.bots.people_counting_bot import PeopleCountingBot

INVALID_SETTINGS_MODULE_NAME = 'tests.invalid_dandy_settings'


class TestVisionBot(TestCase):
    def test_vision_bot(self):
        people_counting_bot = PeopleCountingBot()

        image_intel = people_counting_bot.process(
            Path(settings.BASE_PATH, 'assets', 'images', 'vision_test_image.jpg')
        )

        print(image_intel.people_count)

        self.assertGreater(image_intel.people_count, 2)
