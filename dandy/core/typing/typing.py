from typing import Any

from typing_extensions import Dict, Tuple, NewType

TypedKwargsDict = NewType('TypedKwargsDict', Dict[str, Tuple[type, Any]])