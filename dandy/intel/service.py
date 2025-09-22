from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.intel.mixin import IntelServiceMixin


class IntelService(BaseService['IntelServiceMixin']):
    obj: IntelServiceMixin
