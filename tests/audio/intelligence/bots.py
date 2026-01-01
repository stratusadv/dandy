from pathlib import Path

from dandy import Bot


class TranscriptionBot(Bot):
    def process(self, audio_file_path: Path) -> str:
        return self.audio.transcribe(
            audio_format='mp3',
            audio_file_path=audio_file_path,
        ).text
