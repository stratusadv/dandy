from pathlib import Path
from unittest import TestCase

from dandy.conf import settings
from dandy.processor.bot.bot import Bot

INVALID_SETTINGS_MODULE_NAME = 'tests.invalid_dandy_settings'


class TestAudioService(TestCase):
    def test_transcribe(self):
        bot = Bot()

        transcription_intel = bot.audio.transcribe(
            audio_format='mpeg',
            audio_file_path=Path(
                settings.BASE_PATH, 'assets', 'audio', 'recording.mp3'
            ),
        )

        self.assertGreater(
            len(transcription_intel.text),
            25
        )

    def test_transcribe_with_prompt(self):
        bot = Bot()

        transcription_intel = bot.audio.transcribe(
            prompt='Only return the animals in the text',
            audio_format='mpeg',
            audio_file_path=Path(
                settings.BASE_PATH, 'assets', 'audio', 'recording.mp3'
            ),
        )

        self.assertGreater(
            len(transcription_intel.text),
            25
        )
