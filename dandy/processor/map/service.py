from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.processor.map.map import Map

class MapService(BaseService['Map']):
    obj: Map
