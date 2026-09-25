from typing import Any

from typing import NewType

TypedKwargsDict = NewType('TypedKwargsDict', dict[str, tuple[type, Any]])