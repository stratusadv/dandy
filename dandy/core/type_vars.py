from typing_extensions_extensions import TypeVar

from pydantic import BaseModel


ModelType = TypeVar('ModelType', bound=BaseModel)