from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.map.map import BaseMap

class BotService(BaseService['BaseMap']):
    obj: BaseMap
