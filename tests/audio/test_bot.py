from pathlib import Path
from unittest import TestCase

from dandy.conf import settings
from tests.audio.intelligence.bots import TranscriptionBot

INVALID_SETTINGS_MODULE_NAME = 'tests.invalid_dandy_settings'


class TestAudioBot(TestCase):
    def test_audio_bot(self):
        transcription_bot = TranscriptionBot()

        transcription = transcription_bot.process(
            Path(settings.BASE_PATH, 'assets', 'audio', 'recording.mp3')
        )

        print(transcription)

        self.assertGreater(len(transcription), 25)
