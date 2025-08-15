from dandy.vision.service.service import VisionService


class VisionProcessorMixin:
    vision_config: str = 'DEFAULT'

    vision: VisionService = VisionService()