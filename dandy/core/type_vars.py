from typing_extensions import TypeVar

from pydantic import BaseModel


ModelType = TypeVar('ModelType', bound=BaseModel)