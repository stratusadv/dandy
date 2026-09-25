from dandy.shared.service.mixin import BaseServiceMixin
from dandy.application.llm.tool.service import LlmToolService


class LlmToolServiceMixin(BaseServiceMixin):
    @property
    def tools(self) -> LlmToolService:
        return self._get_service_instance(LlmToolService)

    def reset(self):
        super().reset()
        self.tools.reset()
