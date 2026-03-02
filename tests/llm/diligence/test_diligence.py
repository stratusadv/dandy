
from unittest import TestCase, mock

from tests.llm.diligence.intelligence.bot import CelestialObserverBot


class TestDiligence(TestCase):
    def test_default_diligence(self):

        for int_level in range(21):
            test_bot = CelestialObserverBot(diligence=int_level * 0.1)

            celestial_intel = test_bot.process('What is the large round object that is circling the plant earth, is generally only visible at night and affects the tides?')

            self.assertEqual(celestial_intel.text.lower(), 'moon')


