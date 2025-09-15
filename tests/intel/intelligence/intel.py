from typing import Union

from pydantic import Field

from dandy.intel.intel import BaseIntel, BaseListIntel


class ThingIntel(BaseIntel):
    name: str
    description: str | None = None


class BagIntel(BaseIntel):
    color: str
    stylish: bool
    pockets: Union[int, None] = None
    things: Union[list[ThingIntel], None] = None


class PersonIntel(BaseIntel):
    first_name: str
    last_name: str
    middle_name: Union[str, None] = None
    age: int | None = None
    bag: Union[BagIntel, None] = None


class ThingsIntel(BaseListIntel):
    items: list[ThingIntel] = Field(default_factory=list)