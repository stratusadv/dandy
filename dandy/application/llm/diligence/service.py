from dandy.shared.service.service import BaseService
from dandy.application.llm.diligence.diligence import BaseDiligence
from dandy.application.llm.diligence.handler import DiligenceHandler
from dandy.application.llm.diligence.second_pass.diligence import SecondPassRemovalDiligence
from dandy.application.llm.diligence.stop_word_removal.diligence import StopWordRemovalDiligence
from dandy.application.llm.diligence.vowel_removal.diligence import VowelRemovalDiligence


class DiligenceService(BaseService['dandy.application.llm.diligence.mixin.DiligenceServiceMixin']):
    def __post_init__(self):
        self.post_handler: DiligenceHandler = None
        self.pre_handler: DiligenceHandler = None
        self._reset_handlers()

    def _reset_handlers(self):
        self.post_handler: DiligenceHandler = DiligenceHandler()
        self.pre_handler: DiligenceHandler = DiligenceHandler()

    @property
    def second_pass(self) -> SecondPassRemovalDiligence:
        return self.post_handler.get_diligence(
            SecondPassRemovalDiligence
        )

    @property
    def stop_word_removal(self) -> StopWordRemovalDiligence:
        return self.post_handler.get_diligence(
            StopWordRemovalDiligence
        )

    @property
    def vowel_removal(self) -> VowelRemovalDiligence:
        return self.pre_handler.get_diligence(
            VowelRemovalDiligence
        )

    def reset(self):
        self._reset_handlers()
