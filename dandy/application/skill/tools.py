from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

from dandy.domain.intel.intel import BaseIntel
from dandy.domain.tool.tool import BaseTool

if TYPE_CHECKING:
    from dandy.application.skill.service import SkillService


class SkillMethodTool(BaseTool):
    """A tool that exposes one skill method under a prefixed tool name.

    The wrapped method's typed signature becomes the tool's parameter schema
    (the same mechanism BaseTool uses for its handle).
    """

    def __init__(self, tool_name: str, description: str, method: Callable) -> None:
        self.name = tool_name
        self.description = description
        self._method = method

        super().__init__()

    @property
    def handle(self) -> Callable:
        @wraps(self._method)
        def handle(**kwargs: Any) -> str | BaseIntel:
            return self._method(**kwargs)

        return handle


class ActivateSkillTool(BaseTool):
    name = 'activate_skill'
    description = (
        'Activate a passive skill by name so its instructions are loaded and '
        'its tools become available. The result contains the skill instructions '
        'to follow.'
    )

    def __init__(self, skill_service: 'SkillService') -> None:
        self._skill_service = skill_service

        super().__init__()

    def handle(self, name: str) -> str:
        return self._skill_service.activate(name)
