from unittest import TestCase, mock

from dandy import Recorder
from tests.llm.diligence.intelligence.bot import CelestialObserverBot


class TestDiligence(TestCase):
    def test_default_diligence(self) -> None:

        for int_level in range(21):
            test_bot = CelestialObserverBot(diligence=int_level * 0.1)

            Recorder.start_recording(f'diligence_{int_level}')

            celestial_intel = test_bot.process(
                'What is the large round object that is circling the plant earth, is generally only visible at night and affects the tides?'
            )

            assert celestial_intel.text.lower() == 'moon'

            Recorder.stop_recording(f'diligence_{int_level}')

            if int_level in {0, 21}:
                Recorder.to_html_file(f'diligence_{int_level}')
