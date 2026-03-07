from dandy.core.service.service import BaseService
from dandy.llm.diligence.diligence import BaseDiligence
from dandy.llm.diligence.handler import DiligenceHandler
from dandy.llm.diligence.second_pass.diligence import SecondPassRemovalDiligence
from dandy.llm.diligence.stop_word_removal.diligence import StopWordRemovalDiligence
from dandy.llm.diligence.vowel_removal.diligence import VowelRemovalDiligence


class DiligenceService(BaseService['dandy.llm.diligence.mixin.DiligenceServiceMixin']):
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
