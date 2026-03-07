from unittest import TestCase, mock

from dandy import Recorder
from tests.llm.diligence.intelligence.bot import CelestialObserverBot

QUESTION = 'What is the large round object that is circling the plant earth, is generally only visible at night and affects the tides?'
ANSWER = 'moon'


class TestDiligence(TestCase):
    def setUp(self) -> None:
        self.celestial_observer_bot = CelestialObserverBot()

    def test_default_diligence(self) -> None:
        celestial_intel = self.celestial_observer_bot.process(QUESTION)

        assert celestial_intel.text.lower() == ANSWER

    def test_stop_word_removal_diligence(self) -> None:
        self.celestial_observer_bot.llm.diligence.stop_word_removal.activate()

        celestial_intel = self.celestial_observer_bot.process(QUESTION)

        assert celestial_intel.text.lower() == ANSWER

    def test_vowel_removal_diligence(self) -> None:
        self.celestial_observer_bot.llm.diligence.vowel_removal.activate()
        celestial_intel = self.celestial_observer_bot.process(QUESTION)

        assert celestial_intel.text.lower() == ANSWER

    def test_second_pass_diligence(self) -> None:
        self.celestial_observer_bot.llm.diligence.second_pass.activate()
        celestial_intel = self.celestial_observer_bot.process(QUESTION)

        assert celestial_intel.text.lower() == ANSWER

    def test_all_diligence(self) -> None:
        self.celestial_observer_bot.llm.diligence.stop_word_removal.activate()
        self.celestial_observer_bot.llm.diligence.vowel_removal.activate()
        self.celestial_observer_bot.llm.diligence.second_pass.activate()

        celestial_intel = self.celestial_observer_bot.process(QUESTION)

        assert celestial_intel.text.lower() == ANSWER