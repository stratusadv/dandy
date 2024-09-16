from typing import List, Dict

from pydantic import BaseModel


class LocationModel(BaseModel):
    city: str
    country: str


class PersonModel(BaseModel):
    first_name: str
    last_name: str
    age: int
    hat_description: str
    catch_phrase: str
    funny_facts: List[str]
    travel_locations: List[LocationModel]