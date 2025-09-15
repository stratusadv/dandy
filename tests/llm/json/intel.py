from enum import Enum

from pydantic import Field
from pydantic.fields import FieldInfo

from dandy.intel.intel import BaseIntel


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
