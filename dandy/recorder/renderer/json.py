from pathlib import Path

from dandy.consts import RECORDING_POSTFIX_NAME
from dandy.recorder.renderer.renderer import BaseRecordingRenderer


class JsonRecordingRenderer(BaseRecordingRenderer):
    name: str = 'json'
    file_extension: str = 'json'

    def _render_json_to_str(self) -> str:
        return self.recording.model_dump_json()

    def to_file(
            self,
            path: Path | str,
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

        with open(
                Path(path, f'{self.recording.name}{RECORDING_POSTFIX_NAME}.json'),
                'w',
                encoding='utf-8'
        ) as new_file:
            new_file.write(self.to_str())

    def to_str(self) -> str:
        return self._render_json_to_str()
