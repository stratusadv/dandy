from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel

from dandy.recorder.recording import Recording


class BaseRecordingRenderer(BaseModel, ABC):
    recording: Recording

    @abstractmethod
    def to_file(
            self,
            path: Path,
    ):
        ...

    @abstractmethod
    def to_str(self) -> str:
        ...
