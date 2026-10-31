from dandy.shared.service.mixin import BaseServiceMixin
from dandy.application.skill.service import SkillService


class SkillServiceMixin(BaseServiceMixin):
    @property
    def skills(self) -> SkillService:
        return self._get_service_instance(SkillService)

    def reset(self) -> None:
        super().reset()
        self.skills.reset()
