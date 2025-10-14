import random
import string
from typing import Any

from dandy.intel.intel import BaseIntel


def generate_new_recorder_event_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=4))


def json_default(obj: Any) -> str | dict:
    if isinstance(obj, BaseIntel):
        return obj.model_dump()

    try:
        return str(obj)
    except TypeError:
        return '<unserializable value>'
