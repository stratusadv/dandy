from __future__ import annotations

import hashlib
import json
from pathlib import PurePath
from typing import Any, Callable

from pydantic_core import PydanticSerializationError

# Head and tail characters kept when a long string is reduced in the shallow
# level. Strings of twice this length or shorter pass through unchanged, so
# small payloads keep a true fingerprint while large ones (base64 media, file
# contents) fold down to their length plus their edges.
SHALLOW_STRING_KEEP = 32

# Digest length in hex characters for both hash levels.
HASH_LENGTH = 32


def dump_model(model_dump: Callable[..., Any]) -> Any:
    """A bound JSON-mode ``model_dump`` with a python-mode fallback.

    Some state (for example, an ``Ellipsis`` placeholder inside a schema) is
    not JSON-serializable, so when JSON mode fails the raw python-mode dump
    is used and ``canonicalize`` handles whatever it returns. Pass the
    unoverridden dump (``super().model_dump``) when the class's own
    ``model_dump`` reshapes state for the wire.
    """
    try:
        return model_dump(mode='json')
    except (TypeError, ValueError, PydanticSerializationError):
        return model_dump()


def canonicalize(value: Any, shallow: bool = False) -> Any:
    """Reduce a value to a deterministic JSON-serializable form.

    Whitespace runs in strings fold to a single space, dict keys stringify,
    sets and frozensets sort, paths become strings, classes reduce to their
    module and qualname, and nested Dandy objects (anything carrying a
    ``deep_hash``) stand in as their class name plus digest. In the shallow
    level, long strings additionally reduce to a length plus head and tail
    fingerprint, keeping the digest cheap over large payloads.
    """
    if isinstance(value, str):
        folded = ' '.join(value.split())

        if shallow and len(folded) > SHALLOW_STRING_KEEP * 2:
            return f'{len(folded)}:{folded[:SHALLOW_STRING_KEEP]}...{folded[-SHALLOW_STRING_KEEP:]}'

        value = folded

    elif isinstance(value, dict):
        value = {str(key): canonicalize(item, shallow) for key, item in value.items()}

    elif isinstance(value, (list, tuple)):
        value = [canonicalize(item, shallow) for item in value]

    elif isinstance(value, (set, frozenset)):
        value = sorted((canonicalize(item, shallow) for item in value), key=repr)

    elif isinstance(value, type):
        value = {'__module__': value.__module__, '__qualname__': value.__qualname__}

    elif isinstance(value, PurePath):
        value = str(value)

    elif hasattr(value, 'deep_hash'):
        digest = getattr(value, 'shallow_hash' if shallow else 'deep_hash')()
        value = {'__qualname__': value.__class__.__qualname__, '__digest__': digest}

    elif hasattr(value, 'model_dump'):
        value = canonicalize(dump_model(value.model_dump), shallow)

    return value


def _digest(payload: Any) -> str:
    try:
        serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=repr)
    except (TypeError, ValueError):
        serialized = repr(payload)

    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()[:HASH_LENGTH]


class HashMixin:
    """Two-level state hashing for duplicate detection and cache keys.

    ``shallow_hash`` is the cheap level: the full structure of the state with
    every long string reduced to a length plus head and tail fingerprint, so
    it stays fast over large payloads and can be counted at volume.
    ``deep_hash`` is the exact level: a digest of the fully canonicalized
    state, so two objects share one deep hash only when they hold the same
    state. ``__hash__`` follows the deep level, which makes mixin classes
    usable in sets and as dict keys (plain pydantic models are unhashable, so
    this is what makes them keyable at all). Equality is left to each class's
    own semantics, so for duplicate detection compare ``deep_hash()`` values
    directly rather than relying on set or dict membership alone.
    """

    def hash_state(self) -> Any:
        """The state that both hash levels digest.

        Pydantic models dump to their JSON-mode field values; anything else
        falls back to its instance attributes. Subclasses override this when
        the object's identity lives in class attributes or when the model's
        own dump method reshapes state (for example, to the wire shape).
        """
        if hasattr(self, 'model_dump'):
            return dump_model(self.model_dump)

        return vars(self)

    def shallow_hash(self) -> str:
        """Cheap state digest for high-volume duplicate counting."""
        return _digest([self.__class__.__qualname__, canonicalize(self.hash_state(), shallow=True)])

    def deep_hash(self) -> str:
        """Exact state digest: equal state hashes equal, changed state does not."""
        state = canonicalize(self.hash_state(), shallow=False)
        return _digest([self.__class__.__qualname__, state])

    def __hash__(self) -> int:
        return hash(self.deep_hash())
