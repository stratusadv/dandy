from pathlib import Path

from dandy.consts import RECORDING_POSTFIX_NAME, __VERSION__
from dandy.core.utils import python_obj_to_markdown
from dandy.recorder.renderer.renderer import BaseRecordingRenderer
from dandy.recorder.utils import generate_new_recorder_event_id


class MarkdownRecordingRenderer(BaseRecordingRenderer):
    name: str = 'markdown'
    file_extension: str = 'md'

    def _render_markdown_to_str(self) -> str:
        markdown_str = f'# Dandy v{__VERSION__} Recording Output: {generate_new_recorder_event_id()}\n\n'

        markdown_str += python_obj_to_markdown(
            self.recording.model_dump()
        )

        return markdown_str

    def to_file(
            self,
            path: Path | str,
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

        with open(
                Path(path, f'{self.recording.name}{RECORDING_POSTFIX_NAME}.md'),
                'w',
                encoding='utf-8'
        ) as new_file:
            new_file.write(
                self.to_str()
            )

    def to_str(self) -> str:
        return self._render_markdown_to_str()
