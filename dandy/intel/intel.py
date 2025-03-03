from pydantic import BaseModel
from typing_extensions import Generator, Union, List, Generic, TypeVar

T = TypeVar('T')

class BaseIntel(BaseModel):
    pass


class BaseIterableIntel(BaseIntel, Generic[T]):
    items: List[T]

    def __getitem__(self, index) -> Union[List[T], T]:
        return self.items[index]

    def __iter__(self) -> Generator[T]:
        for item in self.items:
            yield item

    def __setitem__(self, index, value: T):
        self.items[index] = value

    def add(self, item: T):
        self.items.append(item)
