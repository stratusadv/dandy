from dandy.shared.service.mixin import BaseServiceMixin
from dandy.application.tool.service import ToolService


class ToolServiceMixin(BaseServiceMixin):
    @property
    def tools(self) -> ToolService:
        return self._get_service_instance(ToolService)

    def reset(self) -> None:
        super().reset()
        self.tools.reset()
