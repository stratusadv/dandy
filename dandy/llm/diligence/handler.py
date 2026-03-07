from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector
    from dandy.llm.diligence.diligence import BaseDiligence

DiligenceType = TypeVar('DiligenceType', bound='BaseDiligence')


class DiligenceHandler:
    def __init__(self) -> None:
        self._diligence_classes_instances: dict[type[BaseDiligence], BaseDiligence] = {}

    @property
    def is_activated(self) -> bool:
        if not self._diligence_classes_instances:
            return False

        return any(diligence.is_activated for diligence in self._diligence_classes_instances.values())

    def apply(self, llm_connector: LlmConnector) -> None:
        for diligence in self._diligence_classes_instances.values():
            if diligence.is_activated:
                diligence.apply(llm_connector=llm_connector)

    def get_diligence(self, diligence_class: type[DiligenceType]) -> DiligenceType:
        if diligence_class not in self._diligence_classes_instances:
            self._diligence_classes_instances[diligence_class] = diligence_class()

        return self._diligence_classes_instances[diligence_class]

    @property
    def requires_new_llm_request(self) -> bool:
        for diligence in self._diligence_classes_instances.values():
            if diligence.is_activated and diligence.requires_new_llm_request:
                return True

        return False
