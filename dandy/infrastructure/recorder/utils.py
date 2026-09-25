from typing import Any

from dandy.domain.intel.intel import BaseIntel
from dandy.shared.utils import generate_recorder_event_id

__all__ = ['generate_recorder_event_id', 'json_default']


def json_default(obj: Any) -> str | dict:
    if isinstance(obj, BaseIntel):
        return obj.model_dump()

    try:
        return str(obj)
    except TypeError:
        return '<unserializable value>'
