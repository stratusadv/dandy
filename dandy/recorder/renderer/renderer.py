from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel

from dandy.recorder.recording import Recording


class BaseRecordingRenderer(BaseModel, ABC):
    recording: Recording
    name: str
    file_extension: str

    @abstractmethod
    def to_file(
            self,
            path: Path | str,
    ):
        ...

    @abstractmethod
    def to_str(self) -> str:
        ...
