from typing_extensions import TypeVar

from dandy.intel.intel import BaseIntel

IntelType = TypeVar('IntelType', bound=BaseIntel)