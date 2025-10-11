from enum import Enum

from pydantic import Field

from dandy import BaseIntel, BaseListIntel


class ThingIntel(BaseIntel):
    name: str
    description: str | None = None


class BagIntel(BaseIntel):
    color: str
    stylish: bool
    pockets: int | None = None
    things: list[ThingIntel] | None = None


class PersonIntel(BaseIntel):
    first_name: str
    last_name: str
    middle_name: str | None = None
    age: int | None = None
    bag: BagIntel | None = None


class ThingsIntel(BaseListIntel):
    items: list[ThingIntel] = Field(default_factory=list)


class Sector(Enum):
    INDUSTRY = 'industry'
    FINANCE = 'finance'
    SERVICES = 'services'
    HEALTH = 'health'


class OfficeIntel(BaseIntel):
    name: str
    business_sector: Sector
    employees: int = Field(gt=100, lt=200)
    temperature_deg_c: float = Field(gt=17.5, lt=24.9)
    windows: int = Field(gt=632, lt=689)
    happiness_level: float = Field(gt=0.00, lt=9.99)
