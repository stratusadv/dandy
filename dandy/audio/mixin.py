from typing import ClassVar

from dandy.intel.intel import BaseIntel, DefaultIntel

from dandy.audio.config.config import AudioConfig
from dandy.core.service.mixin import BaseServiceMixin
from dandy.audio.service import AudioService


class AudioServiceMixin(BaseServiceMixin):
    audio_config: str | AudioConfig = 'DEFAULT'
    audio_intel_class: type[BaseIntel] = DefaultIntel

    audio: ClassVar[AudioService] = AudioService()
    _AudioService_instance: AudioService | None = None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        audio_config: str | None = kwargs.get('audio_config')

        if audio_config is not None:
            self.audio_config = audio_config

        if isinstance(self.audio_config, str):
            self.audio_config = AudioConfig(self.audio_config)

        self.audio_intel_class = self.__class__.audio_intel_class

        self.audio.set_obj_service_instance(
            self,
            None,
        )

    def reset_services(self):
        super().reset_services()
