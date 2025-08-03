from typing import Any

from typing import Dict, Tuple, NewType

TypedKwargsDict = NewType('TypedKwargsDict', Dict[str, Tuple[type, Any]])